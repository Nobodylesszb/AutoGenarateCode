# 激活码平台 API 集成文档

## 概述

本文档详细说明了如何将激活码平台集成到您的项目中，包括购买流程、验证流程和使用流程。

## 基础配置

### 1. API 基础 URL
```
生产环境: https://your-domain.com/api/v1
开发环境: http://localhost:8000/api/v1
```

### 2. 认证方式
激活码平台使用 JWT 进行身份认证，管理接口需要提供有效的访问令牌。

## 核心流程

### 1. 购买激活码流程

#### 步骤 1: 获取产品信息
```http
GET /api/v1/products
```

响应示例:
```json
[
  {
    "id": 1,
    "product_id": "premium_license",
    "name": "高级版许可证",
    "description": "包含所有高级功能",
    "price": 99.00,
    "currency": "CNY",
    "is_active": true
  }
]
```

#### 步骤 2: 创建支付订单
```http
POST /api/v1/payment/create
Content-Type: application/json

{
  "activation_code_id": 1,
  "method": "wechat",
  "return_url": "https://your-app.com/payment/success"
}
```

响应示例:
```json
{
  "id": 1,
  "payment_id": "PAY_1234567890",
  "activation_code_id": 1,
  "amount": 99.00,
  "currency": "CNY",
  "method": "wechat",
  "status": "pending",
  "payment_url": "https://pay.weixin.qq.com/example",
  "qr_code": "WECHAT_QR_1234567890",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 步骤 3: 跳转支付
```javascript
// 方式 1: 跳转到支付页面
window.location.href = paymentInfo.payment_url;

// 方式 2: 显示二维码
// 使用 qr_code 生成二维码供用户扫描
```

#### 步骤 4: 处理支付回调
支付完成后，系统会自动调用您配置的回调 URL。

### 2. 验证激活码流程

#### 步骤 1: 验证激活码
```http
GET /api/v1/activation/verify/{code}?user_id=user123
```

响应示例:
```json
{
  "valid": true,
  "message": "激活码有效",
  "activation_code": {
    "id": 1,
    "code": "ACT1234567890ABCD",
    "product_id": "premium_license",
    "product_name": "高级版许可证",
    "status": "unused",
    "price": 99.00,
    "currency": "CNY",
    "expires_at": "2025-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 步骤 2: 使用激活码
```http
POST /api/v1/activation/use/{code}
Content-Type: application/json

{
  "user_id": "user123"
}
```

响应示例:
```json
{
  "success": true,
  "message": "激活码使用成功",
  "activation_code": {
    "id": 1,
    "code": "ACT1234567890ABCD",
    "status": "used",
    "used_at": "2024-01-01T12:00:00Z",
    "used_by": "user123"
  }
}
```

## 集成示例

### JavaScript/Node.js 集成

```javascript
class ActivationCodeClient {
  constructor(baseUrl, apiKey = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` }),
        ...options.headers
      },
      ...options
    };
    
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
  
  // 获取产品列表
  async getProducts() {
    return this.request('/api/v1/products');
  }
  
  // 创建支付订单
  async createPayment(activationCodeId, method, returnUrl = null) {
    return this.request('/api/v1/payment/create', {
      method: 'POST',
      body: JSON.stringify({
        activation_code_id: activationCodeId,
        method: method,
        return_url: returnUrl
      })
    });
  }
  
  // 验证激活码
  async verifyCode(code, userId = null) {
    const endpoint = userId 
      ? `/api/v1/activation/verify/${code}?user_id=${userId}`
      : `/api/v1/activation/verify/${code}`;
    return this.request(endpoint);
  }
  
  // 使用激活码
  async useCode(code, userId = null) {
    return this.request(`/api/v1/activation/use/${code}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId })
    });
  }
}

// 使用示例
const client = new ActivationCodeClient('https://your-domain.com');

// 获取产品列表
const products = await client.getProducts();

// 创建支付订单
const payment = await client.createPayment(1, 'wechat', 'https://your-app.com/success');

// 跳转支付
window.location.href = payment.payment_url;
```

### Python 集成

```python
import requests
from typing import Optional, Dict, Any

class ActivationCodeClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        if method == 'GET':
            response = self.session.get(url)
        elif method == 'POST':
            response = self.session.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    def get_products(self) -> list:
        """获取产品列表"""
        return self.request('/api/v1/products')
    
    def create_payment(self, activation_code_id: int, method: str, return_url: Optional[str] = None) -> Dict[str, Any]:
        """创建支付订单"""
        data = {
            'activation_code_id': activation_code_id,
            'method': method
        }
        if return_url:
            data['return_url'] = return_url
            
        return self.request('/api/v1/payment/create', 'POST', data)
    
    def verify_code(self, code: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """验证激活码"""
        endpoint = f'/api/v1/activation/verify/{code}'
        if user_id:
            endpoint += f'?user_id={user_id}'
        return self.request(endpoint)
    
    def use_code(self, code: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """使用激活码"""
        data = {}
        if user_id:
            data['user_id'] = user_id
        return self.request(f'/api/v1/activation/use/{code}', 'POST', data)

# 使用示例
client = ActivationCodeClient('https://your-domain.com')

# 获取产品列表
products = client.get_products()

# 创建支付订单
payment = client.create_payment(1, 'wechat', 'https://your-app.com/success')

# 验证激活码
result = client.verify_code('ACT1234567890ABCD', 'user123')
if result['valid']:
    # 使用激活码
    use_result = client.use_code('ACT1234567890ABCD', 'user123')
    print(f"激活成功: {use_result['message']}")
```

### PHP 集成

```php
<?php
class ActivationCodeClient {
    private $baseUrl;
    private $apiKey;
    
    public function __construct($baseUrl, $apiKey = null) {
        $this->baseUrl = $baseUrl;
        $this->apiKey = $apiKey;
    }
    
    private function request($endpoint, $method = 'GET', $data = null) {
        $url = $this->baseUrl . $endpoint;
        
        $headers = [
            'Content-Type: application/json'
        ];
        
        if ($this->apiKey) {
            $headers[] = 'Authorization: Bearer ' . $this->apiKey;
        }
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($data) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 400) {
            throw new Exception("HTTP error: $httpCode");
        }
        
        return json_decode($response, true);
    }
    
    public function getProducts() {
        return $this->request('/api/v1/products');
    }
    
    public function createPayment($activationCodeId, $method, $returnUrl = null) {
        $data = [
            'activation_code_id' => $activationCodeId,
            'method' => $method
        ];
        
        if ($returnUrl) {
            $data['return_url'] = $returnUrl;
        }
        
        return $this->request('/api/v1/payment/create', 'POST', $data);
    }
    
    public function verifyCode($code, $userId = null) {
        $endpoint = '/api/v1/activation/verify/' . $code;
        if ($userId) {
            $endpoint .= '?user_id=' . urlencode($userId);
        }
        return $this->request($endpoint);
    }
    
    public function useCode($code, $userId = null) {
        $data = [];
        if ($userId) {
            $data['user_id'] = $userId;
        }
        return $this->request('/api/v1/activation/use/' . $code, 'POST', $data);
    }
}

// 使用示例
$client = new ActivationCodeClient('https://your-domain.com');

// 获取产品列表
$products = $client->getProducts();

// 创建支付订单
$payment = $client->createPayment(1, 'wechat', 'https://your-app.com/success');

// 验证激活码
$result = $client->verifyCode('ACT1234567890ABCD', 'user123');
if ($result['valid']) {
    // 使用激活码
    $useResult = $client->useCode('ACT1234567890ABCD', 'user123');
    echo "激活成功: " . $useResult['message'];
}
?>
```

## Webhook 集成

### 支付回调处理

当支付完成时，系统会向您配置的回调 URL 发送 POST 请求。

#### 微信支付回调
```http
POST /your-webhook-url
Content-Type: application/x-www-form-urlencoded

return_code=SUCCESS&result_code=SUCCESS&out_trade_no=PAY_1234567890&transaction_id=4200001234567890&total_fee=9900&time_end=20240101120000&sign=ABC123DEF456
```

#### 支付宝回调
```http
POST /your-webhook-url
Content-Type: application/x-www-form-urlencoded

out_trade_no=PAY_1234567890&trade_no=2024010122001234567890&trade_status=TRADE_SUCCESS&total_amount=99.00&timestamp=2024-01-01 12:00:00&sign=ABC123DEF456
```

### 回调处理示例

```javascript
// Express.js 示例
app.post('/webhook/payment', (req, res) => {
  const callbackData = req.body;
  
  // 验证签名
  if (!verifySignature(callbackData)) {
    return res.status(400).send('Invalid signature');
  }
  
  // 处理支付成功
  if (callbackData.trade_status === 'TRADE_SUCCESS' || 
      callbackData.result_code === 'SUCCESS') {
    
    // 更新订单状态
    updateOrderStatus(callbackData.out_trade_no, 'paid');
    
    // 发送激活码给用户
    sendActivationCodeToUser(callbackData.out_trade_no);
  }
  
  res.send('success');
});
```

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权 | 检查 API 密钥 |
| 404 | 资源不存在 | 检查请求路径 |
| 429 | 请求频率限制 | 降低请求频率 |
| 500 | 服务器内部错误 | 联系技术支持 |

### 错误响应格式

```json
{
  "detail": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 最佳实践

### 1. 安全建议
- 使用 HTTPS 进行所有 API 调用
- 妥善保管 API 密钥
- 验证所有回调签名
- 实施请求频率限制

### 2. 性能优化
- 使用连接池
- 实施缓存策略
- 异步处理长时间操作
- 监控 API 响应时间

### 3. 错误处理
- 实现重试机制
- 记录详细错误日志
- 提供用户友好的错误信息
- 监控系统健康状态

## 技术支持

如有技术问题，请通过以下方式联系：

- 提交 Issue
- 发送邮件至 support@example.com
- 加入技术交流群

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✨ 完整的 API 文档
- ✨ 多语言集成示例
- ✨ Webhook 支持
