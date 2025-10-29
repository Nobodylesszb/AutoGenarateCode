"""
微信支付提供商实现
支持微信H5、APP、JSAPI支付
"""

import uuid
import json
import hashlib
import xml.etree.ElementTree as ET
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from .base import PaymentProvider, PaymentResult, PaymentConfig, PaymentMethod

class WeChatPaymentProvider(PaymentProvider):
    """微信支付提供商"""
    
    def __init__(self, config: PaymentConfig):
        super().__init__(config)
        self.app_id = config.app_id
        self.mch_id = config.merchant_id
        self.api_key = config.api_key
        self.notify_url = config.notify_url
        self.sandbox = config.sandbox
        
        # 根据支付方式设置不同的API端点
        if config.method == PaymentMethod.WECHAT_H5:
            self.trade_type = "MWEB"
            self.api_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        elif config.method == PaymentMethod.WECHAT_APP:
            self.trade_type = "APP"
            self.api_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        elif config.method == PaymentMethod.WECHAT_JSAPI:
            self.trade_type = "JSAPI"
            self.api_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        else:
            self.trade_type = "MWEB"
            self.api_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    
    def create_order(self, payment_id: str, amount: float, description: str, 
                    client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
        """创建微信支付订单"""
        try:
            self._log_payment_event("create_order_start", payment_id, {
                "amount": amount,
                "description": description,
                "client_ip": client_ip,
                "trade_type": self.trade_type
            })
            
            # 如果没有配置，返回模拟结果
            if not self.app_id or not self.mch_id or not self.api_key:
                return self._create_mock_order(payment_id, amount, description)
            
            # 构建请求参数
            params = {
                "appid": self.app_id,
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str(),
                "body": description,
                "out_trade_no": payment_id,
                "total_fee": int(amount * 100),  # 金额单位为分
                "spbill_create_ip": client_ip,
                "notify_url": self.notify_url,
                "trade_type": self.trade_type
            }
            
            # 如果是JSAPI支付，需要添加openid
            if self.trade_type == "JSAPI":
                openid = kwargs.get("openid")
                if not openid:
                    return PaymentResult(
                        success=False,
                        payment_id=payment_id,
                        message="JSAPI支付需要提供openid"
                    )
                params["openid"] = openid
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 转换为XML
            xml_data = self._dict_to_xml(params)
            
            # 发送请求
            response = requests.post(self.api_url, data=xml_data.encode('utf-8'), timeout=30)
            
            if response.status_code == 200:
                result = self._xml_to_dict(response.text)
                if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                    return self._handle_success_response(payment_id, amount, result)
                else:
                    return PaymentResult(
                        success=False,
                        payment_id=payment_id,
                        message=f"微信支付失败: {result.get('err_code_des', '未知错误')}"
                    )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message=f"微信支付请求失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self._log_payment_event("create_order_error", payment_id, {"error": str(e)})
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"创建微信支付订单失败: {str(e)}"
            )
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证微信支付回调"""
        try:
            # 检查必要字段
            required_fields = ["return_code", "result_code", "out_trade_no", "transaction_id", "total_fee", "sign"]
            for field in required_fields:
                if field not in callback_data:
                    self.logger.error(f"微信支付回调缺少必要字段: {field}")
                    return False
            
            # 验证签名
            sign = callback_data.pop("sign", "")
            calculated_sign = self._generate_sign(callback_data)
            
            if sign != calculated_sign:
                self.logger.error("微信支付回调签名验证失败")
                return False
            
            # 验证支付状态
            if callback_data.get("return_code") != "SUCCESS" or callback_data.get("result_code") != "SUCCESS":
                self.logger.error("微信支付回调状态异常")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"微信支付回调验证失败: {str(e)}")
            return False
    
    def query_order(self, payment_id: str) -> PaymentResult:
        """查询微信支付订单状态"""
        try:
            if not self.app_id or not self.mch_id or not self.api_key:
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    message="模拟订单查询成功"
                )
            
            # 构建查询参数
            params = {
                "appid": self.app_id,
                "mch_id": self.mch_id,
                "out_trade_no": payment_id,
                "nonce_str": self._generate_nonce_str()
            }
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 转换为XML
            xml_data = self._dict_to_xml(params)
            
            # 发送查询请求
            query_url = "https://api.mch.weixin.qq.com/pay/orderquery"
            response = requests.post(query_url, data=xml_data.encode('utf-8'), timeout=30)
            
            if response.status_code == 200:
                result = self._xml_to_dict(response.text)
                if result.get("return_code") == "SUCCESS":
                    trade_state = result.get("trade_state")
                    if trade_state == "SUCCESS":
                        return PaymentResult(
                            success=True,
                            payment_id=payment_id,
                            order_id=result.get("transaction_id"),
                            amount=float(result.get("total_fee", 0)) / 100,
                            message="订单支付成功"
                        )
                    else:
                        return PaymentResult(
                            success=False,
                            payment_id=payment_id,
                            message=f"订单状态: {trade_state}"
                        )
                else:
                    return PaymentResult(
                        success=False,
                        payment_id=payment_id,
                        message=f"查询失败: {result.get('return_msg')}"
                    )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message=f"查询请求失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"查询微信支付订单失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"查询订单失败: {str(e)}"
            )
    
    def refund(self, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
        """微信支付退款"""
        try:
            if not self.app_id or not self.mch_id or not self.api_key:
                return PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    amount=amount,
                    message="模拟退款成功"
                )
            
            # 构建退款参数
            params = {
                "appid": self.app_id,
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str(),
                "out_trade_no": payment_id,
                "out_refund_no": f"RF{payment_id}",
                "total_fee": int(amount * 100),
                "refund_fee": int(amount * 100),
                "refund_desc": reason or "用户申请退款"
            }
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 转换为XML
            xml_data = self._dict_to_xml(params)
            
            # 发送退款请求
            refund_url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
            response = requests.post(refund_url, data=xml_data.encode('utf-8'), timeout=30)
            
            if response.status_code == 200:
                result = self._xml_to_dict(response.text)
                if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
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
                        message=f"退款失败: {result.get('err_code_des', '未知错误')}"
                    )
            else:
                return PaymentResult(
                    success=False,
                    payment_id=payment_id,
                    message=f"退款请求失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"微信支付退款失败: {str(e)}")
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
            payment_url=f"https://pay.weixin.qq.com/mock/{payment_id}",
            qr_code=f"WECHAT_QR_{payment_id}",
            amount=amount,
            currency=self.config.extra_config.get("currency", "CNY"),
            message="模拟微信支付成功"
        )
    
    def _handle_success_response(self, payment_id: str, amount: float, result: Dict[str, Any]) -> PaymentResult:
        """处理成功响应"""
        if self.trade_type == "MWEB":
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                payment_url=result.get("mweb_url"),
                amount=amount,
                currency=self.config.extra_config.get("currency", "CNY"),
                message="微信H5支付订单创建成功"
            )
        elif self.trade_type == "APP":
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                extra_data={
                    "appid": self.app_id,
                    "partnerid": self.mch_id,
                    "prepayid": result.get("prepay_id"),
                    "package": "Sign=WXPay",
                    "noncestr": self._generate_nonce_str(),
                    "timestamp": str(int(datetime.now().timestamp()))
                },
                amount=amount,
                currency=self.config.extra_config.get("currency", "CNY"),
                message="微信APP支付订单创建成功"
            )
        elif self.trade_type == "JSAPI":
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                extra_data={
                    "appId": self.app_id,
                    "timeStamp": str(int(datetime.now().timestamp())),
                    "nonceStr": self._generate_nonce_str(),
                    "package": f"prepay_id={result.get('prepay_id')}",
                    "signType": "MD5"
                },
                amount=amount,
                currency=self.config.extra_config.get("currency", "CNY"),
                message="微信JSAPI支付订单创建成功"
            )
        else:
            return PaymentResult(
                success=True,
                payment_id=payment_id,
                payment_url=result.get("mweb_url"),
                amount=amount,
                currency=self.config.extra_config.get("currency", "CNY"),
                message="微信支付订单创建成功"
            )
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        return uuid.uuid4().hex
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 字典排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 拼接字符串
        string_a = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        string_sign_temp = f"{string_a}&key={self.api_key}"
        # MD5加密并转大写
        sign = hashlib.md5(string_sign_temp.encode('utf-8')).hexdigest().upper()
        return sign
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """字典转XML"""
        xml = ["<xml>"]
        for k, v in data.items():
            if isinstance(v, str):
                xml.append(f"<{k}><![CDATA[{v}]]></{k}>")
            else:
                xml.append(f"<{k}>{v}</{k}>")
        xml.append("</xml>")
        return "".join(xml)
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        """XML转字典"""
        root = ET.fromstring(xml_str)
        data = {}
        for child in root:
            data[child.tag] = child.text
        return data
