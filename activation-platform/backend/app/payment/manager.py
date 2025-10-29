"""
支付服务管理器
统一管理所有支付提供商
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from . import (
    PaymentServiceManager, PaymentConfigManager, PaymentEventListener,
    PaymentStatisticsService, PaymentMethod, PaymentConfig, PaymentResult
)
from .providers import register_payment_providers, get_payment_provider_info
from app.config import settings

class PaymentManager:
    """支付管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("payment.manager")
        
        # 初始化各个组件
        self.service_manager = PaymentServiceManager()
        self.config_manager = PaymentConfigManager()
        self.event_listener = PaymentEventListener()
        self.statistics_service = PaymentStatisticsService()
        
        # 注册支付提供商
        self._register_payment_providers()
    
    def _register_payment_providers(self):
        """注册支付提供商"""
        try:
            # 注册微信支付
            wechat_config = PaymentConfig(
                method=PaymentMethod.WECHAT_H5,
                app_id=settings.WECHAT_APP_ID,
                merchant_id=settings.WECHAT_MCH_ID,
                api_key=settings.WECHAT_API_KEY,
                notify_url=settings.WECHAT_NOTIFY_URL,
                sandbox=settings.DEBUG,
                extra_config={"currency": "CNY"}
            )
            self.service_manager.register_provider(PaymentMethod.WECHAT_H5, wechat_config)
            
            # 注册微信APP支付
            wechat_app_config = PaymentConfig(
                method=PaymentMethod.WECHAT_APP,
                app_id=settings.WECHAT_APP_ID,
                merchant_id=settings.WECHAT_MCH_ID,
                api_key=settings.WECHAT_API_KEY,
                notify_url=settings.WECHAT_NOTIFY_URL,
                sandbox=settings.DEBUG,
                extra_config={"currency": "CNY"}
            )
            self.service_manager.register_provider(PaymentMethod.WECHAT_APP, wechat_app_config)
            
            # 注册微信JSAPI支付
            wechat_jsapi_config = PaymentConfig(
                method=PaymentMethod.WECHAT_JSAPI,
                app_id=settings.WECHAT_APP_ID,
                merchant_id=settings.WECHAT_MCH_ID,
                api_key=settings.WECHAT_API_KEY,
                notify_url=settings.WECHAT_NOTIFY_URL,
                sandbox=settings.DEBUG,
                extra_config={"currency": "CNY"}
            )
            self.service_manager.register_provider(PaymentMethod.WECHAT_JSAPI, wechat_jsapi_config)
            
            # 注册支付宝H5支付
            alipay_h5_config = PaymentConfig(
                method=PaymentMethod.ALIPAY_H5,
                app_id=settings.ALIPAY_APP_ID,
                private_key=settings.ALIPAY_PRIVATE_KEY,
                public_key=settings.ALIPAY_PUBLIC_KEY,
                notify_url=settings.ALIPAY_NOTIFY_URL,
                sandbox=settings.DEBUG,
                extra_config={"currency": "CNY"}
            )
            self.service_manager.register_provider(PaymentMethod.ALIPAY_H5, alipay_h5_config)
            
            # 注册支付宝APP支付
            alipay_app_config = PaymentConfig(
                method=PaymentMethod.ALIPAY_APP,
                app_id=settings.ALIPAY_APP_ID,
                private_key=settings.ALIPAY_PRIVATE_KEY,
                public_key=settings.ALIPAY_PUBLIC_KEY,
                notify_url=settings.ALIPAY_NOTIFY_URL,
                sandbox=settings.DEBUG,
                extra_config={"currency": "CNY"}
            )
            self.service_manager.register_provider(PaymentMethod.ALIPAY_APP, alipay_app_config)
            
            # 注册支付宝网页支付
            alipay_web_config = PaymentConfig(
                method=PaymentMethod.ALIPAY_WEB,
                app_id=settings.ALIPAY_APP_ID,
                private_key=settings.ALIPAY_PRIVATE_KEY,
                public_key=settings.ALIPAY_PUBLIC_KEY,
                notify_url=settings.ALIPAY_NOTIFY_URL,
                sandbox=settings.DEBUG,
                extra_config={"currency": "CNY"}
            )
            self.service_manager.register_provider(PaymentMethod.ALIPAY_WEB, alipay_web_config)
            
            # 注册模拟支付
            mock_config = PaymentConfig(
                method=PaymentMethod.MOCK,
                sandbox=True,
                extra_config={
                    "currency": "CNY",
                    "mock_delay": 0,
                    "mock_success_rate": 1.0
                }
            )
            self.service_manager.register_provider(PaymentMethod.MOCK, mock_config)
            
            # 注册 Ping++（若配置完整）
            if getattr(settings, "PINGXX_API_KEY", None):
                pingxx_config = PaymentConfig(
                    method=PaymentMethod.PINGXX,
                    app_id=getattr(settings, "PINGXX_APP_ID", None),
                    api_key=getattr(settings, "PINGXX_API_KEY", None),
                    private_key=getattr(settings, "PINGXX_PRIVATE_KEY", None),
                    notify_url=getattr(settings, "PINGXX_NOTIFY_URL", None),
                    sandbox=settings.DEBUG,
                    extra_config={"currency": "CNY"}
                )
                self.service_manager.register_provider(PaymentMethod.PINGXX, pingxx_config)
            
            self.logger.info("支付提供商注册完成")
            
        except Exception as e:
            self.logger.error(f"支付提供商注册失败: {str(e)}")
    
    def create_payment(self, method: PaymentMethod, amount: float, description: str,
                      client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
        """创建支付订单"""
        return self.service_manager.create_payment(method, amount, description, client_ip, **kwargs)
    
    def verify_callback(self, method: PaymentMethod, callback_data: Dict[str, Any]) -> bool:
        """验证支付回调"""
        return self.service_manager.verify_callback(method, callback_data)
    
    def query_payment(self, method: PaymentMethod, payment_id: str) -> PaymentResult:
        """查询支付状态"""
        return self.service_manager.query_payment(method, payment_id)
    
    def refund_payment(self, method: PaymentMethod, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
        """退款"""
        return self.service_manager.refund_payment(method, payment_id, amount, reason)
    
    def get_supported_methods(self) -> List[Dict[str, Any]]:
        """获取支持的支付方式"""
        methods = self.service_manager.get_supported_methods()
        provider_info = get_payment_provider_info()
        
        result = []
        for method in methods:
            method_value = method.value
            method_name = method_value.split('_')[0]  # wechat, alipay, mock
            
            if method_name in provider_info:
                provider_data = provider_info[method_name]
                for method_info in provider_data["methods"]:
                    if method_info["method"] == method_value:
                        result.append({
                            "method": method_value,
                            "name": method_info["name"],
                            "description": method_info["description"],
                            "provider": provider_data["name"],
                            "enabled": True
                        })
                        break
        
        return result
    
    def get_payment_provider_info(self) -> Dict[str, Any]:
        """获取支付提供商信息"""
        return get_payment_provider_info()
    
    def add_event_listener(self, listener):
        """添加事件监听器"""
        self.event_listener.add_listener(listener)
    
    def remove_event_listener(self, listener):
        """移除事件监听器"""
        self.event_listener.remove_listener(listener)
    
    def notify_event(self, event: str, payment_id: str, data: Dict[str, Any]):
        """通知事件"""
        self.event_listener.notify(event, payment_id, data)
    
    def record_payment_statistics(self, method: PaymentMethod, amount: float, success: bool):
        """记录支付统计"""
        self.statistics_service.record_payment(method, amount, success)
    
    def get_payment_statistics(self) -> Dict[str, Any]:
        """获取支付统计"""
        return self.statistics_service.get_statistics()
    
    def convert_payment_method(self, method_str: str) -> PaymentMethod:
        """转换支付方式字符串为枚举"""
        method_mapping = {
            "wechat": PaymentMethod.WECHAT_H5,
            "wechat_h5": PaymentMethod.WECHAT_H5,
            "wechat_app": PaymentMethod.WECHAT_APP,
            "wechat_jsapi": PaymentMethod.WECHAT_JSAPI,
            "alipay": PaymentMethod.ALIPAY_H5,
            "alipay_h5": PaymentMethod.ALIPAY_H5,
            "alipay_app": PaymentMethod.ALIPAY_APP,
            "alipay_web": PaymentMethod.ALIPAY_WEB,
            "mock": PaymentMethod.MOCK
        }
        return method_mapping.get(method_str.lower(), PaymentMethod.MOCK)
    
    def get_payment_method_name(self, method: PaymentMethod) -> str:
        """获取支付方式名称"""
        names = {
            PaymentMethod.WECHAT_H5: "微信H5支付",
            PaymentMethod.WECHAT_APP: "微信APP支付",
            PaymentMethod.WECHAT_JSAPI: "微信JSAPI支付",
            PaymentMethod.ALIPAY_H5: "支付宝H5支付",
            PaymentMethod.ALIPAY_APP: "支付宝APP支付",
            PaymentMethod.ALIPAY_WEB: "支付宝网页支付",
            PaymentMethod.MOCK: "模拟支付"
        }
        return names.get(method, method.value)
