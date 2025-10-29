"""
支付提供商注册和初始化
"""

from . import PaymentProviderFactory, PaymentMethod
from .wechat import WeChatPaymentProvider
from .alipay import AlipayPaymentProvider
from .mock import MockPaymentProvider
from .pingxx import PingxxPaymentProvider

def register_payment_providers():
    """注册所有支付提供商"""
    
    # 注册微信支付
    PaymentProviderFactory.register_provider(PaymentMethod.WECHAT_H5, WeChatPaymentProvider)
    PaymentProviderFactory.register_provider(PaymentMethod.WECHAT_APP, WeChatPaymentProvider)
    PaymentProviderFactory.register_provider(PaymentMethod.WECHAT_JSAPI, WeChatPaymentProvider)
    
    # 注册支付宝
    PaymentProviderFactory.register_provider(PaymentMethod.ALIPAY_H5, AlipayPaymentProvider)
    PaymentProviderFactory.register_provider(PaymentMethod.ALIPAY_APP, AlipayPaymentProvider)
    PaymentProviderFactory.register_provider(PaymentMethod.ALIPAY_WEB, AlipayPaymentProvider)
    
    # 注册模拟支付
    PaymentProviderFactory.register_provider(PaymentMethod.MOCK, MockPaymentProvider)
    
    # 注册 Ping++
    PaymentProviderFactory.register_provider(PaymentMethod.PINGXX, PingxxPaymentProvider)

def get_payment_provider_info():
    """获取支付提供商信息"""
    return {
        "wechat": {
            "name": "微信支付",
            "methods": [
                {"method": "wechat_h5", "name": "微信H5支付", "description": "适用于手机浏览器"},
                {"method": "wechat_app", "name": "微信APP支付", "description": "适用于微信APP"},
                {"method": "wechat_jsapi", "name": "微信JSAPI支付", "description": "适用于微信内网页"}
            ],
            "config_fields": [
                {"field": "app_id", "name": "应用ID", "required": True},
                {"field": "merchant_id", "name": "商户号", "required": True},
                {"field": "api_key", "name": "API密钥", "required": True},
                {"field": "notify_url", "name": "回调地址", "required": True}
            ]
        },
        "alipay": {
            "name": "支付宝",
            "methods": [
                {"method": "alipay_h5", "name": "支付宝H5支付", "description": "适用于手机浏览器"},
                {"method": "alipay_app", "name": "支付宝APP支付", "description": "适用于支付宝APP"},
                {"method": "alipay_web", "name": "支付宝网页支付", "description": "适用于PC网页"}
            ],
            "config_fields": [
                {"field": "app_id", "name": "应用ID", "required": True},
                {"field": "private_key", "name": "私钥", "required": True},
                {"field": "public_key", "name": "公钥", "required": True},
                {"field": "notify_url", "name": "回调地址", "required": True},
                {"field": "return_url", "name": "返回地址", "required": False}
            ]
        },
        "mock": {
            "name": "模拟支付",
            "methods": [
                {"method": "mock", "name": "模拟支付", "description": "用于测试和开发"}
            ],
            "config_fields": [
                {"field": "mock_delay", "name": "模拟延迟（秒）", "required": False, "default": 0},
                {"field": "mock_success_rate", "name": "模拟成功率", "required": False, "default": 1.0}
            ]
        }
    }

# 自动注册支付提供商
register_payment_providers()
