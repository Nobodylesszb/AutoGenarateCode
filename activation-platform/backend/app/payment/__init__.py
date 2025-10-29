"""
支付模块基础类和接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import uuid
import logging

# 支付状态枚举
class PaymentStatus(Enum):
    PENDING = "pending"      # 待支付
    PROCESSING = "processing"  # 处理中
    SUCCESS = "success"      # 支付成功
    FAILED = "failed"        # 支付失败
    CANCELLED = "cancelled"   # 已取消
    REFUNDED = "refunded"    # 已退款
    EXPIRED = "expired"      # 已过期

# 支付方式枚举
class PaymentMethod(Enum):
    WECHAT_H5 = "wechat_h5"      # 微信H5支付
    WECHAT_APP = "wechat_app"    # 微信APP支付
    WECHAT_JSAPI = "wechat_jsapi" # 微信JSAPI支付
    ALIPAY_H5 = "alipay_h5"      # 支付宝H5支付
    ALIPAY_APP = "alipay_app"    # 支付宝APP支付
    ALIPAY_WEB = "alipay_web"    # 支付宝网页支付
    UNIONPAY = "unionpay"        # 银联支付
    STRIPE = "stripe"            # Stripe支付
    PAYPAL = "paypal"            # PayPal支付
    MOCK = "mock"                # 模拟支付（测试用）
    PINGXX = "pingxx"            # Ping++ 聚合支付

# 支付结果数据类
@dataclass
class PaymentResult:
    success: bool
    payment_id: str
    order_id: Optional[str] = None
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "CNY"
    message: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

# 支付回调数据类
@dataclass
class PaymentCallback:
    payment_id: str
    order_id: str
    status: PaymentStatus
    amount: float
    currency: str
    callback_data: Dict[str, Any]
    timestamp: datetime

# 支付配置数据类
@dataclass
class PaymentConfig:
    method: PaymentMethod
    app_id: Optional[str] = None
    merchant_id: Optional[str] = None
    api_key: Optional[str] = None
    private_key: Optional[str] = None
    public_key: Optional[str] = None
    notify_url: Optional[str] = None
    return_url: Optional[str] = None
    sandbox: bool = False
    extra_config: Optional[Dict[str, Any]] = None

# 抽象支付接口
class PaymentProvider(ABC):
    """支付提供商抽象基类"""
    
    def __init__(self, config: PaymentConfig):
        self.config = config
        self.logger = logging.getLogger(f"payment.{config.method.value}")
    
    @abstractmethod
    def create_order(self, payment_id: str, amount: float, description: str, 
                    client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
        """创建支付订单"""
        pass
    
    @abstractmethod
    def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证支付回调"""
        pass
    
    @abstractmethod
    def query_order(self, payment_id: str) -> PaymentResult:
        """查询订单状态"""
        pass
    
    @abstractmethod
    def refund(self, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
        """退款"""
        pass
    
    def _generate_payment_id(self) -> str:
        """生成支付ID"""
        return f"PAY_{uuid.uuid4().hex[:16].upper()}"
    
    def _log_payment_event(self, event: str, payment_id: str, data: Dict[str, Any]):
        """记录支付事件日志"""
        self.logger.info(f"Payment event: {event}", extra={
            "payment_id": payment_id,
            "method": self.config.method.value,
            "data": data
        })

# 支付提供商工厂
class PaymentProviderFactory:
    """支付提供商工厂"""
    
    _providers = {}
    
    @classmethod
    def create_provider(cls, method: PaymentMethod, config: PaymentConfig) -> PaymentProvider:
        """创建支付提供商实例"""
        provider_class = cls._providers.get(method)
        if not provider_class:
            raise ValueError(f"不支持的支付方式: {method.value}")
        
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, method: PaymentMethod, provider_class: type):
        """注册新的支付提供商"""
        cls._providers[method] = provider_class
    
    @classmethod
    def get_supported_methods(cls) -> List[PaymentMethod]:
        """获取支持的支付方式"""
        return list(cls._providers.keys())

# 支付服务管理器
class PaymentServiceManager:
    """支付服务管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("payment.manager")
        self._providers: Dict[PaymentMethod, PaymentProvider] = {}
        self._configs: Dict[PaymentMethod, PaymentConfig] = {}
    
    def register_provider(self, method: PaymentMethod, config: PaymentConfig):
        """注册支付提供商"""
        try:
            provider = PaymentProviderFactory.create_provider(method, config)
            self._providers[method] = provider
            self._configs[method] = config
            self.logger.info(f"支付提供商注册成功: {method.value}")
        except Exception as e:
            self.logger.error(f"支付提供商注册失败: {method.value}, 错误: {str(e)}")
            raise
    
    def get_provider(self, method: PaymentMethod) -> PaymentProvider:
        """获取支付提供商"""
        provider = self._providers.get(method)
        if not provider:
            raise ValueError(f"未注册的支付方式: {method.value}")
        return provider
    
    def create_payment(self, method: PaymentMethod, amount: float, description: str,
                      client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
        """创建支付订单"""
        try:
            provider = self.get_provider(method)
            payment_id = provider._generate_payment_id()
            
            result = provider.create_order(
                payment_id=payment_id,
                amount=amount,
                description=description,
                client_ip=client_ip,
                **kwargs
            )
            
            self.logger.info(f"支付订单创建: {payment_id}, 结果: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"创建支付订单失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id="",
                message=f"创建支付订单失败: {str(e)}"
            )
    
    def verify_callback(self, method: PaymentMethod, callback_data: Dict[str, Any]) -> bool:
        """验证支付回调"""
        try:
            provider = self.get_provider(method)
            return provider.verify_callback(callback_data)
        except Exception as e:
            self.logger.error(f"验证支付回调失败: {str(e)}")
            return False
    
    def query_payment(self, method: PaymentMethod, payment_id: str) -> PaymentResult:
        """查询支付状态"""
        try:
            provider = self.get_provider(method)
            return provider.query_order(payment_id)
        except Exception as e:
            self.logger.error(f"查询支付状态失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"查询支付状态失败: {str(e)}"
            )
    
    def refund_payment(self, method: PaymentMethod, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
        """退款"""
        try:
            provider = self.get_provider(method)
            return provider.refund(payment_id, amount, reason)
        except Exception as e:
            self.logger.error(f"退款失败: {str(e)}")
            return PaymentResult(
                success=False,
                payment_id=payment_id,
                message=f"退款失败: {str(e)}"
            )
    
    def get_supported_methods(self) -> List[PaymentMethod]:
        """获取支持的支付方式"""
        return list(self._providers.keys())

# 支付配置管理器
class PaymentConfigManager:
    """支付配置管理器"""
    
    def __init__(self):
        self.configs: Dict[PaymentMethod, PaymentConfig] = {}
    
    def load_config(self, method: PaymentMethod, config_data: Dict[str, Any]) -> PaymentConfig:
        """加载支付配置"""
        config = PaymentConfig(
            method=method,
            app_id=config_data.get("app_id"),
            merchant_id=config_data.get("merchant_id"),
            api_key=config_data.get("api_key"),
            private_key=config_data.get("private_key"),
            public_key=config_data.get("public_key"),
            notify_url=config_data.get("notify_url"),
            return_url=config_data.get("return_url"),
            sandbox=config_data.get("sandbox", False),
            extra_config=config_data.get("extra_config", {})
        )
        
        self.configs[method] = config
        return config
    
    def get_config(self, method: PaymentMethod) -> Optional[PaymentConfig]:
        """获取支付配置"""
        return self.configs.get(method)
    
    def get_all_configs(self) -> Dict[PaymentMethod, PaymentConfig]:
        """获取所有支付配置"""
        return self.configs.copy()

# 支付事件监听器
class PaymentEventListener:
    """支付事件监听器"""
    
    def __init__(self):
        self.listeners: List[callable] = []
    
    def add_listener(self, listener: callable):
        """添加事件监听器"""
        self.listeners.append(listener)
    
    def remove_listener(self, listener: callable):
        """移除事件监听器"""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def notify(self, event: str, payment_id: str, data: Dict[str, Any]):
        """通知所有监听器"""
        for listener in self.listeners:
            try:
                listener(event, payment_id, data)
            except Exception as e:
                logging.error(f"支付事件监听器执行失败: {str(e)}")

# 支付统计服务
class PaymentStatisticsService:
    """支付统计服务"""
    
    def __init__(self):
        self.stats = {
            "total_amount": 0.0,
            "total_orders": 0,
            "success_orders": 0,
            "failed_orders": 0,
            "method_stats": {},
            "daily_stats": {}
        }
    
    def record_payment(self, method: PaymentMethod, amount: float, success: bool):
        """记录支付统计"""
        self.stats["total_amount"] += amount
        self.stats["total_orders"] += 1
        
        if success:
            self.stats["success_orders"] += 1
        else:
            self.stats["failed_orders"] += 1
        
        # 按支付方式统计
        method_key = method.value
        if method_key not in self.stats["method_stats"]:
            self.stats["method_stats"][method_key] = {
                "total_amount": 0.0,
                "total_orders": 0,
                "success_orders": 0
            }
        
        self.stats["method_stats"][method_key]["total_amount"] += amount
        self.stats["method_stats"][method_key]["total_orders"] += 1
        if success:
            self.stats["method_stats"][method_key]["success_orders"] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取支付统计"""
        return self.stats.copy()

# 导出主要类和函数
__all__ = [
    "PaymentStatus",
    "PaymentMethod", 
    "PaymentResult",
    "PaymentCallback",
    "PaymentConfig",
    "PaymentProvider",
    "PaymentProviderFactory",
    "PaymentServiceManager",
    "PaymentConfigManager",
    "PaymentEventListener",
    "PaymentStatisticsService"
]
