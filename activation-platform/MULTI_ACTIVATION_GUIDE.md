# 多激活次数功能使用指南

## 🎯 功能概述

激活码平台现在支持**多激活次数**功能，允许一个激活码被多次使用，直到达到设定的最大激活次数。默认情况下，激活码只能使用一次。

## ✨ 主要特性

### 🔢 可变激活次数
- **默认行为**：激活码只能使用1次
- **自定义次数**：可以设置1-1000次激活
- **实时计数**：自动跟踪当前激活次数
- **剩余次数**：实时显示剩余可用次数

### 📝 详细激活记录
- **用户信息**：记录每次激活的用户ID
- **时间戳**：精确记录激活时间
- **设备信息**：可选的设备信息记录
- **IP地址**：可选的IP地址记录

### 🛡️ 安全控制
- **次数限制**：达到最大次数后自动禁用
- **状态管理**：自动更新激活码状态
- **验证机制**：激活前验证剩余次数

## 🔧 API接口

### 1. 生成多激活次数的激活码

```bash
curl -X POST "http://localhost:8000/api/v1/activation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "multi_activation_product",
    "product_name": "多激活次数产品",
    "price": 299.00,
    "quantity": 1,
    "max_activations": 5
  }'
```

**响应示例：**
```json
[
  {
    "id": 1,
    "code": "ACT1234567890ABCDEF",
    "product_id": "multi_activation_product",
    "product_name": "多激活次数产品",
    "status": "unused",
    "price": 299.00,
    "currency": "CNY",
    "max_activations": 5,
    "current_activations": 0,
    "activation_records": null,
    "created_at": "2025-10-29T11:31:50",
    "updated_at": "2025-10-29T11:31:50"
  }
]
```

### 2. 使用激活码（带详细信息）

```bash
curl -X POST "http://localhost:8000/api/v1/activation/use" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ACT1234567890ABCDEF",
    "user_id": "user123",
    "device_info": {
      "platform": "Windows",
      "version": "10"
    },
    "ip_address": "192.168.1.100"
  }'
```

**响应示例：**
```json
{
  "success": true,
  "message": "激活成功，剩余激活次数: 4",
  "activation_code": {
    "id": 1,
    "code": "ACT1234567890ABCDEF",
    "current_activations": 1,
    "max_activations": 5
  },
  "remaining_activations": 4,
  "activation_record": {
    "user_id": "user123",
    "activation_time": "2025-10-29T11:31:50.465227",
    "device_info": {
      "platform": "Windows",
      "version": "10"
    },
    "ip_address": "192.168.1.100"
  }
}
```

### 3. 获取激活记录

```bash
curl "http://localhost:8000/api/v1/activation/records/ACT1234567890ABCDEF"
```

**响应示例：**
```json
{
  "success": true,
  "activation_code": "ACT1234567890ABCDEF",
  "max_activations": 5,
  "current_activations": 3,
  "remaining_activations": 2,
  "records": [
    {
      "user_id": "user1",
      "activation_time": "2025-10-29T11:31:50.465227",
      "device_info": {"device": "device1"},
      "ip_address": "192.168.1.1"
    },
    {
      "user_id": "user2",
      "activation_time": "2025-10-29T11:31:50.467655",
      "device_info": {"device": "device2"},
      "ip_address": "192.168.1.2"
    },
    {
      "user_id": "user3",
      "activation_time": "2025-10-29T11:31:50.469674",
      "device_info": {"device": "device3"},
      "ip_address": "192.168.1.3"
    }
  ]
}
```

### 4. 验证激活码

```bash
curl "http://localhost:8000/api/v1/activation/verify/ACT1234567890ABCDEF"
```

**响应示例：**
```json
{
  "valid": true,
  "message": "激活码有效",
  "activation_code": {
    "id": 1,
    "code": "ACT1234567890ABCDEF",
    "max_activations": 5,
    "current_activations": 3
  },
  "remaining_activations": 2
}
```

## 🖥️ 客户端集成

### Python SDK示例

```python
from client_sdk_example import ActivationCodeClient

# 创建客户端
client = ActivationCodeClient("http://your-server.com")

# 激活软件许可证（支持多激活次数）
result = client.activate_software_license("ACT1234567890ABCDEF", "user123")

if result["success"]:
    print(f"激活成功！剩余激活次数: {result.get('remaining_activations', 0)}")
else:
    print(f"激活失败: {result['message']}")

# 获取激活记录
records = client.get_activation_records("ACT1234567890ABCDEF")
if records["success"]:
    print(f"当前激活次数: {records['current_activations']}")
    print(f"剩余激活次数: {records['remaining_activations']}")
```

### JavaScript/TypeScript示例

```javascript
class ActivationClient {
    async useActivationCode(activationCode, userId, deviceInfo = null, ipAddress = null) {
        try {
            const response = await fetch(`${this.baseUrl}/api/v1/activation/use`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: activationCode,
                    user_id: userId,
                    device_info: deviceInfo,
                    ip_address: ipAddress
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`激活成功！剩余激活次数: ${data.remaining_activations}`);
                return data;
            } else {
                console.error(`激活失败: ${data.message}`);
                return null;
            }
        } catch (error) {
            console.error('激活请求失败:', error);
            return null;
        }
    }
    
    async getActivationRecords(activationCode) {
        try {
            const response = await fetch(`${this.baseUrl}/api/v1/activation/records/${activationCode}`);
            const data = await response.json();
            
            if (data.success) {
                console.log(`当前激活次数: ${data.current_activations}`);
                console.log(`剩余激活次数: ${data.remaining_activations}`);
                return data;
            } else {
                console.error(`获取记录失败: ${data.message}`);
                return null;
            }
        } catch (error) {
            console.error('获取记录请求失败:', error);
            return null;
        }
    }
}
```

## 📊 使用场景

### 1. 家庭共享软件
- **场景**：一个家庭购买软件，需要在多台设备上使用
- **配置**：`max_activations: 5`（支持5台设备）
- **优势**：一次购买，全家使用

### 2. 企业多用户授权
- **场景**：企业购买软件，需要在多台办公电脑上安装
- **配置**：`max_activations: 50`（支持50台电脑）
- **优势**：灵活的用户管理

### 3. 开发者工具
- **场景**：开发者工具需要在多台开发机器上使用
- **配置**：`max_activations: 3`（支持3台开发机）
- **优势**：支持多环境开发

### 4. 游戏激活码
- **场景**：游戏支持多平台或多设备安装
- **配置**：`max_activations: 2`（支持2个平台）
- **优势**：PC和移动端都能使用

## 🔒 安全考虑

### 激活次数限制
- **防止滥用**：限制激活次数防止无限分享
- **合理设置**：根据产品特性设置合适的激活次数
- **监控使用**：通过激活记录监控使用情况

### 激活记录追踪
- **用户追踪**：记录每次激活的用户信息
- **设备追踪**：记录设备信息防止异常使用
- **时间追踪**：记录激活时间便于审计

### 状态管理
- **自动禁用**：达到最大次数后自动禁用
- **状态同步**：实时更新激活码状态
- **验证机制**：激活前验证剩余次数

## 📈 性能优化

### 数据库优化
- **索引优化**：为激活码字段添加索引
- **查询优化**：优化激活记录查询
- **批量操作**：支持批量激活码生成

### 缓存策略
- **激活状态缓存**：缓存激活码状态信息
- **记录缓存**：缓存激活记录减少数据库查询
- **Redis集成**：使用Redis提高性能

## 🛠️ 配置选项

### 环境变量配置

```env
# 激活码配置
ACTIVATION_CODE_LENGTH=32
ACTIVATION_CODE_PREFIX=ACT
ACTIVATION_CODE_EXPIRE_DAYS=365
ACTIVATION_CODE_SALT_KEY=your_salt_key_here

# 多激活次数配置
DEFAULT_MAX_ACTIVATIONS=1
MAX_ALLOWED_ACTIVATIONS=1000

# 安全配置
ENABLE_ACTIVATION_RECORDS=true
RECORD_DEVICE_INFO=true
RECORD_IP_ADDRESS=true
```

### 产品配置示例

```json
{
  "products": [
    {
      "product_id": "basic_software",
      "product_name": "基础软件",
      "price": 99.00,
      "default_max_activations": 1,
      "description": "单次激活软件"
    },
    {
      "product_id": "family_software",
      "product_name": "家庭版软件",
      "price": 199.00,
      "default_max_activations": 5,
      "description": "支持5次激活的家庭版"
    },
    {
      "product_id": "enterprise_software",
      "product_name": "企业版软件",
      "price": 999.00,
      "default_max_activations": 50,
      "description": "支持50次激活的企业版"
    }
  ]
}
```

## 🔍 故障排除

### 常见问题

**Q: 激活码显示已达到最大激活次数**
A: 检查激活码的`max_activations`设置，确认是否已达到限制

**Q: 激活记录显示不完整**
A: 检查`activation_records`字段是否正确存储JSON数据

**Q: 剩余激活次数计算错误**
A: 检查`current_activations`和`max_activations`字段是否正确更新

### 调试方法

```python
# 检查激活码状态
def debug_activation_code(code):
    service = ActivationCodeService(db)
    activation_code = service.get_activation_code(code)
    
    if activation_code:
        print(f"激活码: {activation_code.code}")
        print(f"最大激活次数: {activation_code.max_activations}")
        print(f"当前激活次数: {activation_code.current_activations}")
        print(f"剩余激活次数: {activation_code.max_activations - activation_code.current_activations}")
        print(f"状态: {activation_code.status}")
        
        # 解析激活记录
        if activation_code.activation_records:
            import json
            records = json.loads(activation_code.activation_records)
            print(f"激活记录数量: {len(records)}")
            for i, record in enumerate(records, 1):
                print(f"第{i}次激活: {record['user_id']} - {record['activation_time']}")
    else:
        print("激活码不存在")
```

## 🎯 总结

多激活次数功能为激活码平台提供了更灵活的授权管理：

- ✅ **灵活配置**：支持1-1000次激活
- ✅ **详细记录**：完整的激活历史追踪
- ✅ **安全控制**：自动次数限制和状态管理
- ✅ **易于集成**：完整的API和SDK支持
- ✅ **性能优化**：高效的数据库设计和缓存策略

这个功能特别适合需要多设备、多用户授权的软件产品，为用户提供了更好的使用体验，同时为开发者提供了灵活的授权管理方案。
