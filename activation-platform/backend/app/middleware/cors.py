from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

def setup_cors(app: FastAPI):
    """设置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该指定具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
