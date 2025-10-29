from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DECIMAL as Decimal
from app.database import Base
import enum

class ActivationCodeStatus(enum.Enum):
    """激活码状态枚举"""
    UNUSED = "unused"      # 未使用
    USED = "used"         # 已使用
    EXPIRED = "expired"   # 已过期
    DISABLED = "disabled" # 已禁用

class PaymentStatus(enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"   # 待支付
    PAID = "paid"         # 已支付
    FAILED = "failed"     # 支付失败
    REFUNDED = "refunded" # 已退款

class PaymentMethod(enum.Enum):
    """支付方式枚举"""
    WECHAT = "wechat"     # 微信支付
    ALIPAY = "alipay"     # 支付宝
    MOCK = "mock"         # 模拟支付（测试用）

class ActivationCode(Base):
    """激活码模型"""
    __tablename__ = "activation_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 增加长度支持更长的激活码
    product_id = Column(String(50), nullable=False, index=True)
    product_name = Column(String(100), nullable=False)
    status = Column(Enum(ActivationCodeStatus), default=ActivationCodeStatus.UNUSED)
    price = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="CNY")
    expires_at = Column(DateTime, nullable=True)
    used_at = Column(DateTime, nullable=True)
    used_by = Column(String(100), nullable=True)  # 使用者标识
    metadata_json = Column(Text, nullable=True)  # JSON 格式的额外数据
    # 激活次数相关字段
    max_activations = Column(Integer, default=1, nullable=False)  # 最大激活次数
    current_activations = Column(Integer, default=0, nullable=False)  # 当前激活次数
    activation_records = Column(Text, nullable=True)  # 激活记录JSON
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联支付记录
    payments = relationship("Payment", back_populates="activation_code")

class Payment(Base):
    """支付记录模型"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(100), unique=True, index=True, nullable=False)
    activation_code_id = Column(Integer, ForeignKey("activation_codes.id"), nullable=False)
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="CNY")
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    third_party_order_id = Column(String(100), nullable=True)  # 第三方支付订单号
    callback_data = Column(Text, nullable=True)  # 回调数据
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联激活码
    activation_code = relationship("ActivationCode", back_populates="payments")

class User(Base):
    """用户模型（用于管理后台）"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Product(Base):
    """产品模型"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="CNY")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
