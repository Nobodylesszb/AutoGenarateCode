"""
重新设计的支付服务
使用新的支付提供商架构
"""

import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Payment, ActivationCode, PaymentStatus as ModelPaymentStatus, PaymentMethod as ModelPaymentMethod, ActivationCodeStatus
from app.schemas import PaymentCreate, PaymentCallback, ActivationCodeCreate
from app.config import settings

# 导入新的支付架构
from app.payment.manager import PaymentManager
from app.payment.base import PaymentMethod, PaymentResult

class PaymentService:
    """支付服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("payment.service")
        
        # 初始化支付管理器
        self.payment_manager = PaymentManager(db)
    
    
    def _convert_payment_method(self, method: str) -> PaymentMethod:
        """转换支付方式"""
        return self.payment_manager.convert_payment_method(method)
    
    def _convert_model_payment_method(self, method: PaymentMethod) -> ModelPaymentMethod:
        """转换模型支付方式"""
        method_mapping = {
            PaymentMethod.WECHAT_H5: ModelPaymentMethod.WECHAT,
            PaymentMethod.WECHAT_APP: ModelPaymentMethod.WECHAT,
            PaymentMethod.WECHAT_JSAPI: ModelPaymentMethod.WECHAT,
            PaymentMethod.ALIPAY_H5: ModelPaymentMethod.ALIPAY,
            PaymentMethod.ALIPAY_APP: ModelPaymentMethod.ALIPAY,
            PaymentMethod.ALIPAY_WEB: ModelPaymentMethod.ALIPAY,
            PaymentMethod.MOCK: ModelPaymentMethod.MOCK
        }
        return method_mapping.get(method, ModelPaymentMethod.MOCK)
    
    def _convert_payment_status(self, status: ProviderPaymentStatus) -> ModelPaymentStatus:
        """转换支付状态"""
        status_mapping = {
            ProviderPaymentStatus.PENDING: ModelPaymentStatus.PENDING,
            ProviderPaymentStatus.PROCESSING: ModelPaymentStatus.PENDING,
            ProviderPaymentStatus.SUCCESS: ModelPaymentStatus.PAID,
            ProviderPaymentStatus.FAILED: ModelPaymentStatus.FAILED,
            ProviderPaymentStatus.CANCELLED: ModelPaymentStatus.FAILED,
            ProviderPaymentStatus.REFUNDED: ModelPaymentStatus.REFUNDED,
            ProviderPaymentStatus.EXPIRED: ModelPaymentStatus.FAILED
        }
        return status_mapping.get(status, ModelPaymentStatus.PENDING)
    
    def create_payment_with_activation_code(self, product_id: str, product_name: str, 
                                           price: float, payment_method: str, 
                                           client_ip: str = "127.0.0.1", 
                                           max_activations: int = 1) -> Dict[str, Any]:
        """创建支付并生成激活码"""
        try:
            # 首先生成激活码
            from app.services.activation_service import ActivationCodeService
            
            activation_service = ActivationCodeService(self.db)
            
            activation_request = ActivationCodeCreate(
                product_id=product_id,
                product_name=product_name,
                price=Decimal(str(price)),
                quantity=1,
                max_activations=max_activations
            )
            
            activation_codes = activation_service.create_activation_codes(activation_request)
            activation_code = activation_codes[0]
            
            # 创建支付订单
            provider_method = self._convert_payment_method(payment_method)
            result = self.payment_manager.create_payment(
                method=provider_method,
                amount=price,
                description=f"购买激活码: {product_name}",
                client_ip=client_ip
            )
            
            if not result.success:
                return {
                    "success": False,
                    "message": result.message or "创建支付订单失败"
                }
            
            # 创建支付记录
            payment = Payment(
                payment_id=result.payment_id,
                activation_code_id=activation_code.id,
                amount=activation_code.price,
                currency=activation_code.currency,
                method=self._convert_model_payment_method(provider_method),
                status=ModelPaymentStatus.PENDING
            )
            
            self.db.add(payment)
            self.db.commit()
            
            # 记录统计
            self.statistics_service.record_payment(provider_method, price, True)
            
            # 触发事件
            self.event_listener.notify("payment_created", result.payment_id, {
                "activation_code_id": activation_code.id,
                "amount": price,
                "method": payment_method
            })
            
            return {
                "success": True,
                "payment_id": result.payment_id,
                "activation_code_id": activation_code.id,
                "activation_code": activation_code.code,
                "payment_url": result.payment_url,
                "qr_code": result.qr_code,
                "amount": activation_code.price,
                "currency": activation_code.currency,
                "product_name": activation_code.product_name
            }
            
        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建支付失败: {str(e)}"
            }
    
    def create_payment(self, request: PaymentCreate, client_ip: str = "127.0.0.1") -> Dict[str, Any]:
        """创建支付订单"""
        try:
            # 获取激活码
            activation_code = self.db.query(ActivationCode).filter(
                ActivationCode.id == request.activation_code_id
            ).first()
            
            if not activation_code:
                return {
                    "success": False,
                    "message": "激活码不存在"
                }
            
            # 检查激活码状态
            if activation_code.status != ActivationCodeStatus.UNUSED:
                return {
                    "success": False,
                    "message": "激活码不可用"
                }
            
            # 创建支付订单
            provider_method = self._convert_payment_method(request.method.value)
            result = self.payment_manager.create_payment(
                method=provider_method,
                amount=float(activation_code.price),
                description=f"购买激活码: {activation_code.product_name}",
                client_ip=client_ip
            )
            
            if not result.success:
                return {
                    "success": False,
                    "message": result.message or "创建支付订单失败"
                }
            
            # 创建支付记录
            payment = Payment(
                payment_id=result.payment_id,
                activation_code_id=request.activation_code_id,
                amount=activation_code.price,
                currency=activation_code.currency,
                method=request.method,
                status=ModelPaymentStatus.PENDING
            )
            
            self.db.add(payment)
            self.db.commit()
            
            # 记录统计
            self.statistics_service.record_payment(provider_method, float(activation_code.price), True)
            
            return {
                "success": True,
                "payment_id": result.payment_id,
                "payment_url": result.payment_url,
                "qr_code": result.qr_code,
                "amount": activation_code.price,
                "currency": activation_code.currency
            }
            
        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建支付失败: {str(e)}"
            }
    
    def handle_payment_callback(self, callback_data: PaymentCallback) -> Dict[str, Any]:
        """处理支付回调"""
        try:
            payment = self.db.query(Payment).filter(
                Payment.payment_id == callback_data.payment_id
            ).first()
            
            if not payment:
                return {
                    "success": False,
                    "message": "支付记录不存在"
                }
            
            # 验证回调数据
            provider_method = self._convert_payment_method(payment.method.value)
            is_valid = self.payment_manager.verify_callback(provider_method, callback_data.callback_data)
            
            if not is_valid:
                return {
                    "success": False,
                    "message": "回调数据验证失败"
                }
            
            # 更新支付状态
            if callback_data.status == "SUCCESS":
                payment.status = ModelPaymentStatus.PAID
                payment.paid_at = datetime.utcnow()
                payment.third_party_order_id = callback_data.third_party_order_id
                payment.callback_data = json.dumps(callback_data.callback_data)
                
                # 记录统计
                self.statistics_service.record_payment(provider_method, float(payment.amount), True)
                
                # 触发事件
                self.event_listener.notify("payment_success", payment.payment_id, {
                    "amount": float(payment.amount),
                    "method": payment.method.value
                })
                
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "支付成功"
                }
            else:
                payment.status = ModelPaymentStatus.FAILED
                
                # 记录统计
                self.statistics_service.record_payment(provider_method, float(payment.amount), False)
                
                # 触发事件
                self.event_listener.notify("payment_failed", payment.payment_id, {
                    "amount": float(payment.amount),
                    "method": payment.method.value
                })
                
                self.db.commit()
                
                return {
                    "success": False,
                    "message": "支付失败"
                }
                
        except Exception as e:
            self.logger.error(f"处理支付回调失败: {str(e)}")
            return {
                "success": False,
                "message": f"处理支付回调失败: {str(e)}"
            }
    
    def get_payment_status(self, payment_id: str) -> Optional[Payment]:
        """获取支付状态"""
        return self.db.query(Payment).filter(Payment.payment_id == payment_id).first()
    
    def process_payment_success(self, payment_id: str) -> Dict[str, Any]:
        """处理支付成功后的逻辑"""
        payment = self.get_payment_status(payment_id)
        
        if not payment:
            return {
                "success": False,
                "message": "支付记录不存在"
            }
        
        if payment.status != ModelPaymentStatus.PAID:
            return {
                "success": False,
                "message": "支付未完成"
            }
        
        # 获取激活码
        activation_code = self.db.query(ActivationCode).filter(
            ActivationCode.id == payment.activation_code_id
        ).first()
        
        if not activation_code:
            return {
                "success": False,
                "message": "激活码不存在"
            }
        
        return {
            "success": True,
            "payment_id": payment_id,
            "activation_code": activation_code.code,
            "product_name": activation_code.product_name,
            "amount": payment.amount,
            "paid_at": payment.paid_at
        }
    
    def refund_payment(self, payment_id: str, reason: str = "用户申请退款") -> Dict[str, Any]:
        """退款处理"""
        try:
            payment = self.get_payment_status(payment_id)
            
            if not payment:
                return {
                    "success": False,
                    "message": "支付记录不存在"
                }
            
            if payment.status != ModelPaymentStatus.PAID:
                return {
                    "success": False,
                    "message": "只有已支付的订单才能退款"
                }
            
            # 调用支付提供商退款
            provider_method = self._convert_payment_method(payment.method.value)
            result = self.payment_manager.refund_payment(
                method=provider_method,
                payment_id=payment_id,
                amount=float(payment.amount),
                reason=reason
            )
            
            if result.success:
                # 更新支付状态为已退款
                payment.status = ModelPaymentStatus.REFUNDED
                payment.callback_data = json.dumps({
                    "refund_reason": reason,
                    "refund_time": datetime.utcnow().isoformat()
                })
                
                # 禁用对应的激活码
                activation_code = self.db.query(ActivationCode).filter(
                    ActivationCode.id == payment.activation_code_id
                ).first()
                
                if activation_code:
                    activation_code.status = ActivationCodeStatus.DISABLED
                
                # 触发事件
                self.event_listener.notify("payment_refunded", payment_id, {
                    "amount": float(payment.amount),
                    "reason": reason
                })
                
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "退款处理成功",
                    "refund_amount": payment.amount
                }
            else:
                return {
                    "success": False,
                    "message": result.message or "退款处理失败"
                }
                
        except Exception as e:
            self.logger.error(f"退款处理失败: {str(e)}")
            return {
                "success": False,
                "message": f"退款处理失败: {str(e)}"
            }
    
    def get_payment_statistics(self) -> Dict[str, Any]:
        """获取支付统计信息"""
        try:
            # 从数据库获取统计
            total_amount = self.db.query(func.sum(Payment.amount)).filter(
                Payment.status == ModelPaymentStatus.PAID
            ).scalar() or 0
            
            total_orders = self.db.query(Payment).filter(
                Payment.status == ModelPaymentStatus.PAID
            ).count()
            
            # 今日支付金额
            today = datetime.utcnow().date()
            today_amount = self.db.query(func.sum(Payment.amount)).filter(
                Payment.status == ModelPaymentStatus.PAID,
                func.date(Payment.paid_at) == today
            ).scalar() or 0
            
            # 今日支付订单数量
            today_orders = self.db.query(Payment).filter(
                Payment.status == ModelPaymentStatus.PAID,
                func.date(Payment.paid_at) == today
            ).count()
            
            # 支付方式统计
            payment_method_stats = self.db.query(
                Payment.method,
                func.count(Payment.id).label('count'),
                func.sum(Payment.amount).label('amount')
            ).filter(
                Payment.status == ModelPaymentStatus.PAID
            ).group_by(Payment.method).all()
            
            # 获取内存中的统计
            memory_stats = self.statistics_service.get_statistics()
            
            return {
                "total_amount": float(total_amount),
                "total_orders": total_orders,
                "today_amount": float(today_amount),
                "today_orders": today_orders,
                "payment_method_stats": [
                    {
                        "method": stat.method.value,
                        "count": stat.count,
                        "amount": float(stat.amount)
                    }
                    for stat in payment_method_stats
                ],
                "memory_stats": memory_stats
            }
            
        except Exception as e:
            self.logger.error(f"获取支付统计失败: {str(e)}")
            return {
                "total_amount": 0.0,
                "total_orders": 0,
                "today_amount": 0.0,
                "today_orders": 0,
                "payment_method_stats": [],
                "memory_stats": {}
            }
    
    def get_supported_payment_methods(self) -> List[Dict[str, Any]]:
        """获取支持的支付方式"""
        try:
            return self.payment_manager.get_supported_methods()
        except Exception as e:
            self.logger.error(f"获取支付方式失败: {str(e)}")
            return []
    
    def add_payment_event_listener(self, listener: callable):
        """添加支付事件监听器"""
        self.payment_manager.add_event_listener(listener)
    
    def remove_payment_event_listener(self, listener: callable):
        """移除支付事件监听器"""
        self.payment_manager.remove_event_listener(listener)