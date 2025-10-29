"""
模拟支付提供商实现
用于测试和开发环境
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from .base import PaymentProvider, PaymentResult, PaymentConfig, PaymentMethod

class MockPaymentProvider(PaymentProvider):
    """模拟支付提供商（用于测试）"""
    
    def __init__(self, config: PaymentConfig):
        super().__init__(config)
        self.mock_delay = config.extra_config.get("mock_delay", 0)  # 模拟延迟（秒）
        self.mock_success_rate = config.extra_config.get("mock_success_rate", 1.0)  # 模拟成功率
    
    def create_order(self, payment_id: str, amount: float, description: str, 
                    client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
        """创建模拟支付订单"""
        try:
            self._log_payment_event("create_order_start", payment_id, {
                "amount": amount,
                "description": description,
                "client_ip": client_ip,
                "mock_delay": self.mock_delay,
                "mock_success_rate": self.mock_success_rate
            })
            
            # 模拟延迟
            if self.mock_delay > 0:
                import time
                time.sleep(self.mock_delay)
            
            # 模拟成功率
            import random
            if random.random() > self.mock_success_rate:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message="模拟支付失败（随机失败）"
                )
            
            # 生成模拟支付信息
            mock_payment_url = f"https://mock-payment.com/pay/{payment_id}"
            mock_qr_code = f"MOCK_QR_{payment_id}"
            
            # 根据支付方式生成不同的模拟信息
            if self.config.method == PaymentMethod.WECHAT_H5:
                mock_payment_url = f"https://pay.weixin.qq.com/mock/{payment_id}"
                mock_qr_code = f"WECHAT_MOCK_QR_{payment_id}"
            elif self.config.method == PaymentMethod.ALIPAY_H5:
                mock_payment_url = f"https://openapi.alipay.com/mock/{payment_id}"
                mock_qr_code = f"ALIPAY_MOCK_QR_{payment_id}"
            
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                payment_url=mock_payment_url,
                qr_code=mock_qr_code,
                amount=amount,
                currency=self.config.extra_config.get("currency", "CNY"),
                message="模拟支付订单创建成功",
                extra_data={
                    "mock_info": {
                        "created_at": datetime.now().isoformat(),
                        "mock_delay": self.mock_delay,
                        "mock_success_rate": self.mock_success_rate,
                        "client_ip": client_ip
                    }
                }
            )
            
        except Exception as e:
            self._log_payment_event("create_order_error", payment_id, {"error": str(e)})
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"创建模拟支付订单失败: {str(e)}"
            )
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证模拟支付回调"""
        try:
            # 模拟支付总是验证成功
            self.logger.info("模拟支付回调验证成功")
            return True
            
        except Exception as e:
            self.logger.error(f"模拟支付回调验证失败: {str(e)}")
            return False
    
    def query_order(self, payment_id: str) -> PaymentResult:
        """查询模拟支付订单状态"""
        try:
            # 模拟订单查询
            import random
            
            # 随机返回不同的状态
            statuses = ["SUCCESS", "PENDING", "FAILED"]
            mock_status = random.choice(statuses)
            
            if mock_status == "SUCCESS":
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    order_id=f"MOCK_ORDER_{payment_id}",
                    amount=100.0,  # 模拟金额
                    message="模拟订单支付成功"
                )
            elif mock_status == "PENDING":
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message="模拟订单待支付"
                )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message="模拟订单支付失败"
                )
                
        except Exception as e:
            self.logger.error(f"查询模拟支付订单失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"查询模拟订单失败: {str(e)}"
            )
    
    def refund(self, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
        """模拟支付退款"""
        try:
            # 模拟退款处理
            import random
            
            # 模拟退款成功率
            if random.random() > 0.9:  # 90%成功率
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    amount=amount,
                    message="模拟退款成功"
                )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message="模拟退款失败（随机失败）"
                )
                
        except Exception as e:
            self.logger.error(f"模拟支付退款失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"模拟退款失败: {str(e)}"
            )
    
    def simulate_payment_success(self, payment_id: str) -> PaymentResult:
        """模拟支付成功（用于测试）"""
        try:
            self._log_payment_event("simulate_payment_success", payment_id, {
                "simulated_at": datetime.now().isoformat()
            })
            
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                order_id=f"MOCK_SUCCESS_{payment_id}",
                amount=100.0,
                message="模拟支付成功"
            )
            
        except Exception as e:
            self.logger.error(f"模拟支付成功失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"模拟支付成功失败: {str(e)}"
            )
    
    def simulate_payment_failure(self, payment_id: str, reason: str = "模拟失败") -> PaymentResult:
        """模拟支付失败（用于测试）"""
        try:
            self._log_payment_event("simulate_payment_failure", payment_id, {
                "reason": reason,
                "simulated_at": datetime.now().isoformat()
            })
            
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"模拟支付失败: {reason}"
            )
            
        except Exception as e:
            self.logger.error(f"模拟支付失败失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"模拟支付失败失败: {str(e)}"
            )
