"""
支付宝支付提供商实现
支持支付宝H5、APP、网页支付
"""

import uuid
import json
import hashlib
import base64
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlencode

from . import PaymentProvider, PaymentResult, PaymentConfig, PaymentMethod

class AlipayPaymentProvider(PaymentProvider):
    """支付宝支付提供商"""
    
    def __init__(self, config: PaymentConfig):
        super().__init__(config)
        self.app_id = config.app_id
        self.private_key = config.private_key
        self.public_key = config.public_key
        self.notify_url = config.notify_url
        self.return_url = config.return_url
        self.sandbox = config.sandbox
        
        # 根据支付方式设置不同的API端点
        if config.method == PaymentMethod.ALIPAY_H5:
            self.method_name = "alipay.trade.wap.pay"
            self.api_url = "https://openapi.alipay.com/gateway.do"
        elif config.method == PaymentMethod.ALIPAY_APP:
            self.method_name = "alipay.trade.app.pay"
            self.api_url = "https://openapi.alipay.com/gateway.do"
        elif config.method == PaymentMethod.ALIPAY_WEB:
            self.method_name = "alipay.trade.page.pay"
            self.api_url = "https://openapi.alipay.com/gateway.do"
        else:
            self.method_name = "alipay.trade.wap.pay"
            self.api_url = "https://openapi.alipay.com/gateway.do"
        
        # 沙箱环境URL
        if self.sandbox:
            self.api_url = "https://openapi.alipaydev.com/gateway.do"
    
    def create_order(self, payment_id: str, amount: float, description: str, 
                    client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
        """创建支付宝支付订单"""
        try:
            self._log_payment_event("create_order_start", payment_id, {
                "amount": amount,
                "description": description,
                "client_ip": client_ip,
                "method_name": self.method_name
            })
            
            # 如果没有配置，返回模拟结果
            if not self.app_id or not self.private_key:
                return self._create_mock_order(payment_id, amount, description)
            
            # 构建请求参数
            params = {
                "app_id": self.app_id,
                "method": self.method_name,
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "notify_url": self.notify_url,
                "biz_content": json.dumps({
                    "out_trade_no": payment_id,
                    "total_amount": str(amount),
                    "subject": description,
                    "product_code": self._get_product_code(),
                    "quit_url": self.return_url or "https://www.alipay.com"
                })
            }
            
            # 如果是网页支付，添加return_url
            if self.method_name == "alipay.trade.page.pay" and self.return_url:
                params["return_url"] = self.return_url
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 构建请求URL
            if self.method_name in ["alipay.trade.wap.pay", "alipay.trade.page.pay"]:
                # H5和网页支付返回支付URL
                payment_url = f"{self.api_url}?{urlencode(params)}"
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    payment_url=payment_url,
                    amount=amount,
                    currency=self.config.extra_config.get("currency", "CNY"),
                    message="支付宝支付订单创建成功"
                )
            else:
                # APP支付返回订单字符串
                order_string = urlencode(params)
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    extra_data={"order_string": order_string},
                    amount=amount,
                    currency=self.config.extra_config.get("currency", "CNY"),
                    message="支付宝APP支付订单创建成功"
                )
                
        except Exception as e:
            self._log_payment_event("create_order_error", payment_id, {"error": str(e)})
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"创建支付宝订单失败: {str(e)}"
            )
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证支付宝回调"""
        try:
            # 检查必要字段
            required_fields = ["out_trade_no", "trade_no", "trade_status", "total_amount", "sign"]
            for field in required_fields:
                if field not in callback_data:
                    self.logger.error(f"支付宝回调缺少必要字段: {field}")
                    return False
            
            # 验证签名
            sign = callback_data.pop("sign", "")
            if not self._verify_sign(callback_data, sign):
                self.logger.error("支付宝回调签名验证失败")
                return False
            
            # 验证支付状态
            trade_status = callback_data.get("trade_status")
            if trade_status not in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                self.logger.error(f"支付宝支付状态异常: {trade_status}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"支付宝回调验证失败: {str(e)}")
            return False
    
    def query_order(self, payment_id: str) -> PaymentResult:
        """查询支付宝订单状态"""
        try:
            if not self.app_id or not self.private_key:
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    message="模拟订单查询成功"
                )
            
            # 构建查询参数
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.query",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps({
                    "out_trade_no": payment_id
                })
            }
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 发送查询请求
            response = requests.post(self.api_url, data=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                trade_query_response = result.get("alipay_trade_query_response", {})
                
                if trade_query_response.get("code") == "10000":
                    trade_status = trade_query_response.get("trade_status")
                    if trade_status == "TRADE_SUCCESS":
                        return PaymentResult(
                            success=True,
                            payment_id=payment_id,
                            order_id=trade_query_response.get("trade_no"),
                            amount=float(trade_query_response.get("total_amount", 0)),
                            message="订单支付成功"
                        )
                    else:
                        return PaymentResult(
                            success=False,
                            payment_id=payment_id,
                            message=f"订单状态: {trade_status}"
                        )
                else:
                    return PaymentResult(
                        success=False,
                        payment_id=payment_id,
                        message=f"查询失败: {trade_query_response.get('sub_msg')}"
                    )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message=f"查询请求失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"查询支付宝订单失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"查询订单失败: {str(e)}"
            )
    
    def refund(self, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
        """支付宝退款"""
        try:
            if not self.app_id or not self.private_key:
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    amount=amount,
                    message="模拟退款成功"
                )
            
            # 构建退款参数
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.refund",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps({
                    "out_trade_no": payment_id,
                    "refund_amount": str(amount),
                    "refund_reason": reason or "用户申请退款"
                })
            }
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 发送退款请求
            response = requests.post(self.api_url, data=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                refund_response = result.get("alipay_trade_refund_response", {})
                
                if refund_response.get("code") == "10000":
                    return PaymentResult(
                        success=True,
                        payment_id=payment_id,
                        amount=amount,
                        message="退款申请成功"
                    )
                else:
                    return PaymentResult(
                        success=False,
                        payment_id=payment_id,
                        message=f"退款失败: {refund_response.get('sub_msg')}"
                    )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message=f"退款请求失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"支付宝退款失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"退款失败: {str(e)}"
            )
    
    def _create_mock_order(self, payment_id: str, amount: float, description: str) -> PaymentResult:
        """创建模拟订单"""
        return PaymentResult(
            success=True,
            payment_id=payment_id,
            payment_url=f"https://openapi.alipay.com/mock/{payment_id}",
            qr_code=f"ALIPAY_QR_{payment_id}",
            amount=amount,
            currency=self.config.extra_config.get("currency", "CNY"),
            message="模拟支付宝支付成功"
        )
    
    def _get_product_code(self) -> str:
        """获取产品码"""
        if self.method_name == "alipay.trade.wap.pay":
            return "QUICK_WAP_PAY"
        elif self.method_name == "alipay.trade.app.pay":
            return "QUICK_MSECURITY_PAY"
        elif self.method_name == "alipay.trade.page.pay":
            return "FAST_INSTANT_TRADE_PAY"
        else:
            return "QUICK_WAP_PAY"
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 这里简化实现，实际项目中需要使用RSA2签名
        # 为了演示，我们使用简单的MD5签名
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        string_a = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        sign = hashlib.md5(string_a.encode('utf-8')).hexdigest()
        return sign
    
    def _verify_sign(self, params: Dict[str, Any], sign: str) -> bool:
        """验证签名"""
        # 这里简化实现，实际项目中需要使用RSA2验证
        calculated_sign = self._generate_sign(params)
        return sign == calculated_sign
