from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from app.config import settings
from app.database import engine, Base
from app.api import activation, payment, webhook
from app.middleware.auth import get_current_user
from app.middleware.cors import setup_cors

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="激活码平台 API",
    description="自动生成激活码平台后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 设置 CORS
setup_cors(app)

# 安全认证
security = HTTPBearer()

# 注册路由
app.include_router(
    activation.router,
    prefix="/api/v1/activation",
    tags=["激活码管理"]
)

app.include_router(
    payment.router,
    prefix="/api/v1/payment",
    tags=["支付管理"]
)

app.include_router(
    webhook.router,
    prefix="/api/v1/webhook",
    tags=["Webhook"]
)

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "激活码平台 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


