# 快速启动指南

## 🚀 立即运行项目

### 方法一：使用启动脚本（推荐）

```bash
# 进入后端目录
cd activation-platform/backend

# 安装依赖
pip install -r requirements.txt

# 运行测试脚本
python test.py

# 启动服务器
python start.py
```

### 方法二：手动启动

```bash
# 进入后端目录
cd activation-platform/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 方法三：使用Docker

```bash
# 在项目根目录
cd activation-platform

# 启动所有服务
docker-compose up -d
```

## 📍 访问地址

启动成功后，可以通过以下地址访问：

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **管理界面**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 🧪 测试API

### 1. 健康检查
```bash
curl http://localhost:8000/health
```

### 2. 生成激活码
```bash
curl -X POST "http://localhost:8000/api/v1/activation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "test_product",
    "product_name": "测试产品",
    "price": 99.00,
    "quantity": 1
  }'
```

### 3. 验证激活码
```bash
curl "http://localhost:8000/api/v1/activation/verify/ACT1234567890ABCD"
```

## 🔧 配置说明

### 数据库配置
项目默认使用SQLite数据库，无需额外配置。数据库文件会自动创建在 `activation_platform.db`。

### 支付配置
测试环境下使用模拟支付，无需真实的支付配置。

### 环境变量
可以通过 `.env` 文件或环境变量进行配置：

```env
# 数据库配置
DATABASE_URL=sqlite:///./activation_platform.db

# JWT配置
SECRET_KEY=your-secret-key

# 调试模式
DEBUG=true
```

## 🐛 常见问题

### 1. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. 端口被占用
```bash
# 查看端口占用
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uvicorn app.main:app --reload --port 8001
```

### 3. 数据库错误
```bash
# 删除数据库文件重新创建
rm activation_platform.db
python test.py
```

## 📱 前端启动

如果需要启动前端界面：

```bash
# 进入前端目录
cd activation-platform/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端地址: http://localhost:3000

## 🔍 调试模式

启动调试模式可以看到详细的日志信息：

```bash
uvicorn app.main:app --reload --log-level debug
```

## 📊 监控和日志

- 日志文件: `logs/app.log`
- 实时日志: 控制台输出
- 健康检查: http://localhost:8000/health
