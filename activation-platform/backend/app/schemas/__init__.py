from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.models import ActivationCodeStatus, PaymentStatus, PaymentMethod

class ActivationCodeBase(BaseModel):
    """激活码基础模式"""
    product_id: str = Field(..., description="产品ID")
    product_name: str = Field(..., description="产品名称")
    price: Decimal = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="额外数据")
    max_activations: int = Field(1, ge=1, le=1000, description="最大激活次数")

class ActivationCodeCreate(ActivationCodeBase):
    """创建激活码请求"""
    quantity: int = Field(1, ge=1, le=1000, description="生成数量")

class ActivationCodeResponse(ActivationCodeBase):
    """激活码响应"""
    id: int
    code: str
    status: ActivationCodeStatus
    used_at: Optional[datetime]
    used_by: Optional[str]
    current_activations: int = 0
    activation_records: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ActivationCodeVerify(BaseModel):
    """激活码验证请求"""
    code: str = Field(..., description="激活码")
    user_id: Optional[str] = Field(None, description="用户ID")

class ActivationCodeVerifyResponse(BaseModel):
    """激活码验证响应"""
    valid: bool
    message: str
    activation_code: Optional[ActivationCodeResponse] = None
    remaining_activations: Optional[int] = None  # 剩余激活次数

class ActivationRecord(BaseModel):
    """激活记录"""
    user_id: str
    activation_time: datetime
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None

class ActivationCodeUseRequest(BaseModel):
    """激活码使用请求"""
    code: str = Field(..., description="激活码")
    user_id: str = Field(..., description="用户ID")
    device_info: Optional[Dict[str, Any]] = Field(None, description="设备信息")
    ip_address: Optional[str] = Field(None, description="IP地址")

class PaymentCreate(BaseModel):
    """创建支付请求"""
    activation_code_id: int = Field(..., description="激活码ID")
    method: PaymentMethod = Field(..., description="支付方式")
    return_url: Optional[str] = Field(None, description="支付完成返回URL")

class PaymentResponse(BaseModel):
    """支付响应"""
    id: int
    payment_id: str
    activation_code_id: int
    amount: Decimal
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    third_party_order_id: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime
    
    # 支付相关字段
    payment_url: Optional[str] = None  # 支付链接
    qr_code: Optional[str] = None      # 二维码
    
    class Config:
        from_attributes = True

class PaymentCallback(BaseModel):
    """支付回调数据"""
    payment_id: str
    third_party_order_id: str
    status: str
    amount: Decimal
    callback_data: Dict[str, Any]

class PaymentCreateWithProduct(BaseModel):
    """创建支付请求（带产品信息）"""
    product_id: str = Field(..., description="产品ID")
    product_name: str = Field(..., description="产品名称")
    price: Decimal = Field(..., description="价格")
    method: PaymentMethod = Field(..., description="支付方式")
    max_activations: int = Field(1, ge=1, le=1000, description="最大激活次数")
    return_url: Optional[str] = Field(None, description="支付完成返回URL")

class PaymentSuccessResponse(BaseModel):
    """支付成功响应"""
    success: bool
    payment_id: str
    activation_code: str
    product_name: str
    amount: Decimal
    paid_at: datetime

class PaymentRefundRequest(BaseModel):
    """退款请求"""
    payment_id: str = Field(..., description="支付ID")
    reason: str = Field("用户申请退款", description="退款原因")

class PaymentStatistics(BaseModel):
    """支付统计"""
    total_amount: float
    total_orders: int
    today_amount: float
    today_orders: int
    payment_method_stats: List[Dict[str, Any]]

class ProductBase(BaseModel):
    """产品基础模式"""
    product_id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    price: Decimal = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币")

class ProductCreate(ProductBase):
    """创建产品请求"""
    pass

class ProductResponse(ProductBase):
    """产品响应"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"

class HardwareBindingRequest(BaseModel):
    """硬件绑定请求"""
    activation_code: str = Field(..., description="激活码")
    hardware_fingerprint: str = Field(..., description="硬件指纹")
    user_id: Optional[str] = Field(None, description="用户ID")

class HardwareBindingResponse(BaseModel):
    """硬件绑定响应"""
    success: bool
    message: str
    binding_info: Optional[Dict[str, Any]] = None

class HardwareVerificationRequest(BaseModel):
    """硬件验证请求"""
    activation_code: str = Field(..., description="激活码")
    hardware_fingerprint: str = Field(..., description="硬件指纹")

class HardwareVerificationResponse(BaseModel):
    """硬件验证响应"""
    valid: bool
    message: str
    binding_info: Optional[Dict[str, Any]] = None

class HardwareUnbindRequest(BaseModel):
    """硬件解绑请求"""
    activation_code: str = Field(..., description="激活码")
    admin_key: str = Field(..., description="管理员密钥")

class HardwareFingerprintResponse(BaseModel):
    """硬件指纹响应"""
    fingerprint: str
    device_info: Dict[str, Any]
    generated_at: datetime

class UnifiedActivationRequest(BaseModel):
    """统一激活码请求"""
    activation_code: str = Field(..., description="激活码")
    product_type: str = Field(..., description="产品类型: software 或 hardware_bound")
    hardware_fingerprint: Optional[str] = Field(None, description="硬件指纹（硬件绑定产品必需）")
    user_id: Optional[str] = Field(None, description="用户ID")

class UnifiedActivationResponse(BaseModel):
    """统一激活码响应"""
    success: bool
    message: str
    activation_type: str  # "software" 或 "hardware_bound"
    activation_code: Optional[Dict[str, Any]] = None
    binding_info: Optional[Dict[str, Any]] = None

class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None
