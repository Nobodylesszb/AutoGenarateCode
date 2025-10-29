# 激活码平台使用指南

## 🎯 系统概述

激活码平台现在支持两套激活码系统，可以根据不同的业务需求选择使用：

### 1. 软件激活码系统（批量生成）
- ✅ 支持批量生成激活码
- ✅ 适合预生成和分发
- ✅ 支持离线验证
- ✅ 简单易用

### 2. 硬件绑定激活码系统（客户端生成）
- ✅ 激活码与硬件唯一绑定
- ✅ 防止激活码被分享
- ✅ 需要客户端生成硬件指纹
- ✅ 在线验证

## 🔧 管理员操作

### 批量生成软件激活码

```bash
# 生成100个基础软件激活码
curl -X POST "http://localhost:8000/api/v1/activation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "basic_software",
    "product_name": "基础软件",
    "price": 99.00,
    "quantity": 100
  }'

# 生成50个高级软件激活码
curl -X POST "http://localhost:8000/api/v1/activation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "premium_software",
    "product_name": "高级软件",
    "price": 299.00,
    "quantity": 50
  }'
```

### 查看激活码统计

```bash
# 查看所有激活码统计
curl "http://localhost:8000/api/v1/activation/stats"

# 查看特定产品激活码统计
curl "http://localhost:8000/api/v1/activation/stats?product_id=basic_software"
```

## 🖥️ 客户端集成

### 软件激活码使用流程

```python
from client_sdk_example import ActivationCodeClient

# 创建客户端
client = ActivationCodeClient("http://your-server.com")

# 激活软件许可证
result = client.activate_software_license("ACT1234567890ABCDEF", "user123")

if result["success"]:
    print("激活成功！")
    print(f"产品: {result['activation_code']['product_name']}")
else:
    print(f"激活失败: {result['message']}")
```

### 硬件绑定激活码使用流程

```python
# 激活硬件绑定许可证
result = client.activate_hardware_bound_license("ACT1234567890ABCDEF", "user123")

if result["success"]:
    print("硬件绑定激活成功！")
    print(f"硬件指纹: {result['hardware_fingerprint']}")
else:
    print(f"激活失败: {result['message']}")

# 验证硬件绑定
verify_result = client.verify_hardware_bound_license("ACT1234567890ABCDEF")

if verify_result["valid"]:
    print("硬件验证通过！")
else:
    print(f"验证失败: {verify_result['message']}")
```

### 统一激活接口使用

```python
# 根据产品类型自动选择激活方式
result = client.unified_activation(
    activation_code="ACT1234567890ABCDEF",
    product_type="software",  # 或 "hardware_bound"
    user_id="user123"
)

if result["success"]:
    print(f"激活成功！类型: {result['activation_type']}")
else:
    print(f"激活失败: {result['message']}")
```

## 📱 前端集成示例

### JavaScript/TypeScript 集成

```javascript
class ActivationClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async generateHardwareFingerprint() {
        // 生成硬件指纹的简化版本
        const deviceInfo = {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screen: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
        
        const fingerprint = await crypto.subtle.digest(
            'SHA-256',
            new TextEncoder().encode(JSON.stringify(deviceInfo))
        );
        
        return Array.from(new Uint8Array(fingerprint))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }
    
    async activateSoftwareLicense(activationCode, userId = null) {
        try {
            // 验证激活码
            const verifyResponse = await fetch(
                `${this.baseUrl}/api/v1/activation/verify/${activationCode}`
            );
            const verifyData = await verifyResponse.json();
            
            if (!verifyData.valid) {
                return { success: false, message: verifyData.message };
            }
            
            // 使用激活码
            const useResponse = await fetch(
                `${this.baseUrl}/api/v1/activation/use/${activationCode}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId })
                }
            );
            const useData = await useResponse.json();
            
            return {
                success: useData.success,
                message: useData.message,
                activation_type: 'software'
            };
            
        } catch (error) {
            return { success: false, message: error.message };
        }
    }
    
    async activateHardwareBoundLicense(activationCode, userId = null) {
        try {
            // 生成硬件指纹
            const hardwareFingerprint = await this.generateHardwareFingerprint();
            
            // 绑定激活码到硬件
            const bindResponse = await fetch(
                `${this.baseUrl}/api/v1/activation/hardware/bind`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        activation_code: activationCode,
                        hardware_fingerprint: hardwareFingerprint,
                        user_id: userId
                    })
                }
            );
            const bindData = await bindResponse.json();
            
            return {
                success: bindData.success,
                message: bindData.message,
                activation_type: 'hardware_bound',
                hardware_fingerprint: hardwareFingerprint
            };
            
        } catch (error) {
            return { success: false, message: error.message };
        }
    }
}

// 使用示例
const client = new ActivationClient();

// 软件激活码激活
client.activateSoftwareLicense('ACT1234567890ABCDEF', 'user123')
    .then(result => {
        if (result.success) {
            console.log('软件激活成功！');
        } else {
            console.error('激活失败:', result.message);
        }
    });

// 硬件绑定激活码激活
client.activateHardwareBoundLicense('ACT1234567890ABCDEF', 'user123')
    .then(result => {
        if (result.success) {
            console.log('硬件绑定激活成功！');
        } else {
            console.error('激活失败:', result.message);
        }
    });
```

## 🔄 产品配置

### 产品类型定义

```json
{
  "products": [
    {
      "product_id": "basic_software",
      "product_name": "基础软件",
      "price": 99.00,
      "requires_hardware_binding": false,
      "description": "标准软件激活码，支持批量生成"
    },
    {
      "product_id": "premium_software",
      "product_name": "高级软件",
      "price": 299.00,
      "requires_hardware_binding": true,
      "description": "硬件绑定激活码，防止盗版"
    },
    {
      "product_id": "enterprise_software",
      "product_name": "企业软件",
      "price": 999.00,
      "requires_hardware_binding": true,
      "description": "企业级软件，严格硬件绑定"
    }
  ]
}
```

## 🛡️ 安全考虑

### 软件激活码系统
- **适用场景**：一般软件、工具软件
- **安全级别**：中等
- **防分享能力**：有限
- **使用便利性**：高

### 硬件绑定系统
- **适用场景**：高价值软件、企业软件、游戏
- **安全级别**：高
- **防分享能力**：强
- **使用便利性**：中等

## 📊 性能对比

| 特性 | 软件激活码 | 硬件绑定 |
|------|------------|----------|
| 生成速度 | 快 | 中等 |
| 验证速度 | 快 | 中等 |
| 存储需求 | 低 | 中等 |
| 网络依赖 | 低 | 高 |
| 安全性 | 中等 | 高 |

## 🔧 故障排除

### 常见问题

**Q: 软件激活码验证失败**
A: 检查激活码格式是否正确，是否已被使用

**Q: 硬件绑定失败**
A: 检查硬件指纹是否有效，设备是否已绑定其他激活码

**Q: 统一激活接口返回错误**
A: 检查产品类型参数是否正确

### 调试方法

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试硬件指纹生成
client = ActivationCodeClient()
fingerprint = client.generate_hardware_fingerprint()
print(f"硬件指纹: {fingerprint}")

# 测试网络连接
try:
    response = requests.get("http://localhost:8000/health")
    print(f"服务器状态: {response.status_code}")
except Exception as e:
    print(f"连接失败: {e}")
```

## 🚀 部署建议

### 生产环境配置

```env
# 激活码配置
ACTIVATION_CODE_LENGTH=32
ACTIVATION_CODE_PREFIX=ACT
ENABLE_HARDWARE_BINDING=true

# 安全配置
ADMIN_UNBIND_KEY=your_secure_admin_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/activation_platform
```

### 负载均衡

- 使用Nginx进行负载均衡
- 配置Redis缓存提高性能
- 设置数据库连接池

## 📈 监控和日志

### 关键指标监控

- 激活码生成数量
- 激活成功率
- 硬件绑定成功率
- API响应时间
- 错误率

### 日志记录

- 所有激活操作
- 硬件绑定操作
- 错误和异常
- 安全事件

## 🎯 总结

激活码平台提供了灵活的双重激活码系统：

1. **软件激活码系统**：适合一般软件，支持批量生成，使用简单
2. **硬件绑定系统**：适合高价值软件，安全性高，防止盗版

您可以根据不同的产品需求选择使用相应的激活码系统，或者使用统一接口让系统自动选择最合适的激活方式。
