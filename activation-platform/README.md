# 激活码平台

一个完整的自动生成激活码平台，支持多种支付方式，具有高度的可扩展性和易用性。

## 🚀 项目特色

- **安全可靠**: 采用先进的加密算法，确保激活码的安全性和唯一性
- **多种支付**: 支持微信支付、支付宝等多种支付方式
- **易于集成**: 提供完整的 RESTful API，方便其他项目对接
- **管理后台**: 提供直观的管理界面，支持激活码管理和数据统计
- **高度可扩展**: 模块化设计，易于扩展新功能

## 📋 功能特性

### 核心功能
- ✅ 激活码生成和管理
- ✅ 多种支付方式集成
- ✅ 激活码验证和使用
- ✅ 支付状态跟踪
- ✅ 数据统计和分析

### 管理功能
- ✅ 激活码批量生成
- ✅ 支付记录查看
- ✅ 产品管理
- ✅ 用户管理
- ✅ 系统统计

### 技术特性
- ✅ RESTful API 设计
- ✅ JWT 身份认证
- ✅ 数据库事务支持
- ✅ 异步任务处理
- ✅ 日志记录
- ✅ 错误处理

## 🏗️ 技术架构

### 后端技术栈
- **框架**: FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **ORM**: SQLAlchemy
- **认证**: JWT
- **支付**: 微信支付、支付宝支付
- **部署**: Docker

### 前端技术栈
- **框架**: Vue 3
- **路由**: Vue Router
- **状态管理**: Pinia
- **构建工具**: Vite
- **样式**: CSS3

## 📁 项目结构

```
activation-platform/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── middleware/     # 中间件
│   ├── tests/              # 测试文件
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile          # Docker 配置
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面组件
│   │   ├── api/           # API 服务
│   │   └── router/        # 路由配置
│   ├── package.json       # Node.js 依赖
│   └── Dockerfile         # Docker 配置
├── docs/                   # 项目文档
├── deployment/            # 部署配置
└── docker-compose.yml     # Docker Compose 配置
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (可选)

### 本地开发

#### 1. 克隆项目
```bash
git clone <repository-url>
cd activation-platform
```

#### 2. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# 编辑 .env 文件，配置数据库和支付信息
uvicorn app.main:app --reload
```

#### 3. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

#### 4. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### Docker 部署

#### 1. 使用 Docker Compose
```bash
docker-compose up -d
```

#### 2. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000

## 📚 API 文档

### 激活码管理

#### 生成激活码
```http
POST /api/v1/activation/generate
Content-Type: application/json

{
  "product_id": "premium_license",
  "product_name": "高级版许可证",
  "price": 99.00,
  "quantity": 10,
  "expires_at": "2025-12-31T23:59:59Z"
}
```

#### 验证激活码
```http
GET /api/v1/activation/verify/{code}?user_id=user123
```

#### 使用激活码
```http
POST /api/v1/activation/use/{code}
Content-Type: application/json

{
  "user_id": "user123"
}
```

### 支付管理

#### 创建支付订单
```http
POST /api/v1/payment/create
Content-Type: application/json

{
  "activation_code_id": 1,
  "method": "wechat",
  "return_url": "http://example.com/success"
}
```

#### 获取支付状态
```http
GET /api/v1/payment/status/{payment_id}
```

## 🔧 配置说明

### 环境变量配置

#### 数据库配置
```env
DATABASE_URL=postgresql://user:password@localhost:5432/activation_platform
```

#### Redis 配置
```env
REDIS_URL=redis://localhost:6379/0
```

#### JWT 配置
```env
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 支付配置
```env
# 微信支付
WECHAT_APP_ID=your-wechat-app-id
WECHAT_MCH_ID=your-wechat-merchant-id
WECHAT_API_KEY=your-wechat-api-key

# 支付宝
ALIPAY_APP_ID=your-alipay-app-id
ALIPAY_PRIVATE_KEY=your-alipay-private-key
```

## 🔌 集成指南

### 其他项目对接

#### 1. 购买激活码
```javascript
// 创建支付订单
const response = await fetch('/api/v1/payment/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    activation_code_id: activationCodeId,
    method: 'wechat'
  })
});

const paymentInfo = await response.json();
// 跳转到支付页面
window.location.href = paymentInfo.payment_url;
```

#### 2. 验证激活码
```javascript
// 验证激活码
const response = await fetch(`/api/v1/activation/verify/${code}`);
const result = await response.json();

if (result.valid) {
  // 激活码有效，可以使用
  console.log('激活码有效:', result.activation_code);
} else {
  // 激活码无效
  console.error('激活码无效:', result.message);
}
```

#### 3. 使用激活码
```javascript
// 使用激活码
const response = await fetch(`/api/v1/activation/use/${code}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: 'user123'
  })
});

const result = await response.json();
if (result.success) {
  // 激活成功
  console.log('激活成功');
}
```

## 🧪 测试

### 运行测试
```bash
cd backend
pytest
```

### 测试覆盖率
```bash
pytest --cov=app --cov-report=html
```

## 📈 性能优化

### 数据库优化
- 使用适当的索引
- 实现查询缓存
- 使用连接池

### 缓存策略
- Redis 缓存热点数据
- API 响应缓存
- 静态资源缓存

### 前端优化
- 代码分割
- 图片懒加载
- 组件缓存

## 🔒 安全考虑

### 数据安全
- 激活码加密存储
- 敏感信息脱敏
- SQL 注入防护

### 接口安全
- JWT 身份认证
- 请求频率限制
- 输入验证

### 支付安全
- 签名验证
- 回调验证
- 订单状态检查

## 🚀 部署指南

### 生产环境部署

#### 1. 服务器要求
- Ubuntu 20.04+ / CentOS 8+
- 4GB+ RAM
- 50GB+ 存储空间

#### 2. 安装依赖
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. 配置环境
```bash
# 复制配置文件
cp env.example .env
# 编辑配置文件
nano .env
```

#### 4. 启动服务
```bash
docker-compose up -d
```

#### 5. 配置 Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 🤝 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 (Python)
- 使用 ESLint (JavaScript)
- 编写单元测试
- 更新文档

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 加入讨论群

## 🔄 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✨ 支持激活码生成和管理
- ✨ 集成微信支付和支付宝
- ✨ 提供管理后台
- ✨ 完整的 API 接口
