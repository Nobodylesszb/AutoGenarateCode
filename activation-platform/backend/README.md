# 激活码平台后端服务

## 项目结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py             # 配置管理
│   ├── database.py           # 数据库连接
│   ├── models/               # 数据模型
│   │   ├── __init__.py
│   │   ├── activation.py     # 激活码模型
│   │   ├── payment.py        # 支付模型
│   │   └── user.py           # 用户模型
│   ├── schemas/              # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── activation.py
│   │   ├── payment.py
│   │   └── user.py
│   ├── services/             # 业务逻辑
│   │   ├── __init__.py
│   │   ├── activation_service.py
│   │   ├── payment_service.py
│   │   └── notification_service.py
│   ├── api/                  # API 路由
│   │   ├── __init__.py
│   │   ├── activation.py
│   │   ├── payment.py
│   │   └── webhook.py
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   ├── crypto.py         # 加密工具
│   │   ├── validators.py     # 验证工具
│   │   └── generators.py     # 激活码生成器
│   └── middleware/           # 中间件
│       ├── __init__.py
│       ├── auth.py
│       └── cors.py
├── tests/                    # 测试文件
├── requirements.txt          # Python 依赖
├── Dockerfile               # Docker 配置
└── README.md                # 项目说明
```

## 核心功能
1. **激活码生成**: 支持多种生成策略和格式
2. **支付集成**: 支持多种支付方式 (微信、支付宝等)
3. **API 接口**: RESTful API 设计，易于集成
4. **Webhook**: 支付回调处理
5. **管理后台**: 激活码管理和统计
6. **安全机制**: JWT 认证、数据加密、防刷机制

## 技术栈
- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **消息队列**: Celery
- **支付**: 微信支付、支付宝支付
- **部署**: Docker + Docker Compose


