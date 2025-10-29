from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "激活码平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./activation_platform.db"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 支付配置
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_MCH_ID: Optional[str] = None
    WECHAT_API_KEY: Optional[str] = None
    WECHAT_NOTIFY_URL: Optional[str] = None
    
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None
    ALIPAY_NOTIFY_URL: Optional[str] = None
    
    # Ping++ 配置
    PINGXX_API_KEY: Optional[str] = None
    PINGXX_APP_ID: Optional[str] = None
    PINGXX_PRIVATE_KEY: Optional[str] = None  # 私钥内容或路径
    PINGXX_NOTIFY_URL: Optional[str] = None
    
    # 激活码配置
    ACTIVATION_CODE_LENGTH: int = 32  # 增加长度到32位
    ACTIVATION_CODE_PREFIX: str = "ACT"
    ACTIVATION_CODE_EXPIRE_DAYS: int = 365
    ACTIVATION_CODE_SALT_KEY: str = "activation_platform_salt_2024"  # 加盐密钥
    
    # 安全配置
    MAX_ACTIVATION_ATTEMPTS: int = 5
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 硬件绑定配置
    ENABLE_HARDWARE_BINDING: bool = True
    ADMIN_UNBIND_KEY: str = "admin_unbind_key_2024"  # 管理员解绑密钥
    HARDWARE_TOLERANCE: float = 0.8  # 硬件指纹相似度容忍度
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 管理后台默认账号（首次登录自动创建）
    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_EMAIL: str = "admin@example.com"
    ADMIN_DEFAULT_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()


