# 支付架构重构文档

## 概述

本次重构将支付功能从单一的服务类拆分为模块化的架构，提高了代码的可维护性和可扩展性。

## 新架构设计

### 1. 目录结构

```
app/payment/
├── __init__.py          # 包初始化文件
├── base.py             # 支付提供商基类
├── wechat.py           # 微信支付实现
├── alipay.py           # 支付宝实现
├── mock.py             # 模拟支付实现
├── providers.py        # 支付提供商工厂
└── manager.py          # 支付管理器
```

### 2. 核心组件

#### 2.1 PaymentProvider (base.py)
- 抽象基类，定义所有支付提供商必须实现的接口
- 包含支付创建、回调处理、订单查询、退款等核心方法
- 提供统一的错误处理和日志记录

#### 2.2 PaymentProviderFactory (providers.py)
- 支付提供商工厂类
- 负责注册和获取支付提供商实例
- 支持动态添加新的支付方式

#### 2.3 PaymentManager (manager.py)
- 支付管理器，统一管理所有支付提供商
- 提供统一的支付接口
- 处理支付事件和监听器

#### 2.4 具体支付实现
- **WeChatPaymentProvider** (wechat.py): 微信支付实现
- **AlipayPaymentProvider** (alipay.py): 支付宝实现
- **MockPaymentProvider** (mock.py): 模拟支付实现

### 3. 设计优势

#### 3.1 模块化
- 每个支付方式独立实现
- 易于维护和测试
- 降低代码耦合度

#### 3.2 可扩展性
- 新增支付方式只需实现 PaymentProvider 接口
- 无需修改现有代码
- 支持动态注册支付提供商

#### 3.3 统一接口
- 所有支付方式使用相同的接口
- 简化业务逻辑
- 提高代码复用性

#### 3.4 事件驱动
- 支持支付事件监听
- 便于集成第三方系统
- 支持异步处理

## 使用方法

### 1. 获取支持的支付方式

```python
payment_service = PaymentService(db)
methods = payment_service.get_supported_payment_methods()
```

### 2. 创建支付订单

```python
payment_data = {
    "product_id": "product_001",
    "product_name": "测试产品",
    "amount": 9.99,
    "currency": "CNY",
    "method": "wechat",  # 或 "alipay", "mock"
    "buyer_id": "buyer_001",
    "buyer_name": "测试用户",
    "description": "测试订单"
}

result = payment_service.create_payment(payment_data, client_ip)
```

### 3. 处理支付回调

```python
callback_data = {
    "payment_id": "payment_001",
    "status": "success",
    "third_party_order_id": "wx_order_001",
    "paid_at": "2024-01-01T12:00:00Z"
}

result = payment_service.handle_payment_callback(callback_data)
```

### 4. 查询支付状态

```python
status = payment_service.get_payment_status("payment_001")
```

### 5. 处理退款

```python
refund_data = {
    "payment_id": "payment_001",
    "reason": "用户申请退款",
    "amount": 9.99
}

result = payment_service.refund_payment(refund_data)
```

## 扩展新的支付方式

### 1. 创建新的支付提供商

```python
# app/payment/new_payment.py
from app.payment.base import PaymentProvider, PaymentResult, PaymentStatus

class NewPaymentProvider(PaymentProvider):
    def __init__(self):
        super().__init__("new_payment")
    
    def create_payment(self, payment_data: dict) -> PaymentResult:
        # 实现支付创建逻辑
        pass
    
    def handle_callback(self, callback_data: dict) -> PaymentResult:
        # 实现回调处理逻辑
        pass
    
    def query_order(self, payment_id: str) -> PaymentResult:
        # 实现订单查询逻辑
        pass
    
    def refund(self, payment_id: str, amount: float, reason: str) -> PaymentResult:
        # 实现退款逻辑
        pass
```

### 2. 注册新的支付提供商

```python
# app/payment/providers.py
from app.payment.new_payment import NewPaymentProvider

# 在 PaymentProviderFactory 中添加
factory.register_provider("new_payment", NewPaymentProvider())
```

### 3. 更新支付方式枚举

```python
# app/payment/providers.py
class PaymentMethod(enum.Enum):
    WECHAT_H5 = "wechat_h5"
    WECHAT_APP = "wechat_app"
    WECHAT_JSAPI = "wechat_jsapi"
    ALIPAY_H5 = "alipay_h5"
    ALIPAY_APP = "alipay_app"
    ALIPAY_WEB = "alipay_web"
    MOCK = "mock"
    NEW_PAYMENT = "new_payment"  # 新增
```

## 配置说明

### 1. 微信支付配置

```python
# app/config.py
WECHAT_APP_ID = "your_wechat_app_id"
WECHAT_MCH_ID = "your_wechat_mch_id"
WECHAT_API_KEY = "your_wechat_api_key"
WECHAT_NOTIFY_URL = "https://your-domain.com/api/v1/payment/wechat/callback"
```

### 2. 支付宝配置

```python
# app/config.py
ALIPAY_APP_ID = "your_alipay_app_id"
ALIPAY_PRIVATE_KEY = "your_alipay_private_key"
ALIPAY_PUBLIC_KEY = "your_alipay_public_key"
ALIPAY_NOTIFY_URL = "https://your-domain.com/api/v1/payment/alipay/callback"
```

## 测试

### 1. 运行测试脚本

```bash
cd activation-platform/backend
python test_new_payment_architecture.py
```

### 2. 测试内容

- 获取支持的支付方式
- 创建模拟支付订单
- 获取支付状态
- 验证激活码
- 测试微信支付（模拟）
- 测试支付宝（模拟）
- 获取支付统计
- 获取支付列表

## 注意事项

1. **配置检查**: 确保支付配置正确设置
2. **错误处理**: 所有支付操作都有完善的错误处理
3. **日志记录**: 重要操作都有详细的日志记录
4. **安全性**: 支付回调验证和签名校验
5. **测试**: 新增支付方式前请充分测试

## 迁移指南

### 从旧架构迁移

1. **更新导入**: 确保所有相关文件都使用新的支付服务
2. **配置检查**: 验证支付配置是否正确
3. **测试验证**: 运行测试脚本确保功能正常
4. **逐步切换**: 建议先在测试环境验证后再切换到生产环境

### 兼容性

- 保持原有API接口不变
- 数据库结构无需修改
- 前端代码无需修改
- 配置文件格式保持不变

## 总结

新的支付架构提供了更好的模块化、可扩展性和可维护性。通过抽象基类和工厂模式，我们可以轻松地添加新的支付方式，而无需修改现有代码。这种设计使得支付系统更加灵活和健壮。