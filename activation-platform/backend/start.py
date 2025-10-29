#!/usr/bin/env python3
"""
激活码平台启动脚本
用于快速启动和测试项目
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 创建环境变量文件...")
        env_content = """# 激活码平台环境配置
APP_NAME=激活码平台
APP_VERSION=1.0.0
DEBUG=true

# 数据库配置 (使用SQLite进行快速测试)
DATABASE_URL=sqlite:///./activation_platform.db

# Redis配置 (可选，测试时可以不使用)
# REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=test-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 支付配置 (测试时使用模拟数据)
WECHAT_APP_ID=test-app-id
WECHAT_MCH_ID=test-mch-id
WECHAT_API_KEY=test-api-key
WECHAT_NOTIFY_URL=http://localhost:8000/api/v1/webhook/payment/wechat

ALIPAY_APP_ID=test-app-id
ALIPAY_PRIVATE_KEY=test-private-key
ALIPAY_PUBLIC_KEY=test-public-key
ALIPAY_NOTIFY_URL=http://localhost:8000/api/v1/webhook/payment/alipay

# 激活码配置
ACTIVATION_CODE_LENGTH=16
ACTIVATION_CODE_PREFIX=ACT
ACTIVATION_CODE_EXPIRE_DAYS=365

# 安全配置
MAX_ACTIVATION_ATTEMPTS=5
RATE_LIMIT_PER_MINUTE=60

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
        env_file.write_text(env_content, encoding='utf-8')
        print("✅ 环境变量文件已创建")
    else:
        print("✅ 环境变量文件已存在")

def create_logs_dir():
    """创建日志目录"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ 日志目录已创建")

def start_server():
    """启动服务器"""
    print("🚀 启动激活码平台服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔄 管理界面: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止服务器\n")
    
    try:
        # 启动FastAPI服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

def main():
    """主函数"""
    print("🎯 激活码平台启动检查")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建必要文件
    create_env_file()
    create_logs_dir()
    
    print("\n✅ 所有检查通过，准备启动服务器...")
    time.sleep(1)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
