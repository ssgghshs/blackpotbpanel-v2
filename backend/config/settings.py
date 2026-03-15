from pydantic_settings import BaseSettings
from typing import Optional
from datetime import timezone


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./db/app.db"
    
    # 脚本数据库配置
    SCRIPT_DATABASE_URL: str = "sqlite:///./db/scripts.db"
    
    # 容器数据库配置
    CONTAINER_DATABASE_URL: str = "sqlite:///./db/container.db"
    
    # 防火墙数据库配置
    FIREWALL_DATABASE_URL: str = "sqlite:///./db/firewall.db"
    
    # 应用配置
    APP_NAME: str = "BlackPotBPanel"
    DEBUG: bool = False
    VERSION: str = "0.0.2"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    
    # 时区配置
    TIMEZONE: str = "UTC"
    
    # API文档配置
    ENABLE_DOCS: bool = True
    
    # 用户界面配置
    LANGUAGE: str = "zh-CN"
    THEME: str = "dark"
    LOGIN_NOTIFY: bool = True
    # 回收站配置
    RECYCLE: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # SSL配置
    SSL_ENABLED: bool = False
    SSL_CERT_PATH: str = "./data/ssl/ssl.crt"
    SSL_KEY_PATH: str = "./data/ssl/ssl.key"

    class Config:
        env_file = "../setting.conf"


settings = Settings()