import secrets
from typing import List, Union
from pydantic import Field, AnyHttpUrl, PostgresDsn, validator, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 基本配置
    PROJECT_NAME: str = "SmartFlow"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # JWT 签名算法
    ALGORITHM: str = "HS256"
    
    # CORS设置
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:8000", "http://localhost:3000"]
    
    # 数据库配置
    # POSTGRES_SERVER: str = "localhost"
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "postgres"
    # POSTGRES_DB: str = "smartflow"
    # DATABASE_URI: str = ""

    # 数据库配置 - 使用 SQLite 而不是 PostgreSQL(已注释)
    DATABASE_URI: str = "sqlite:///./smartflow.db"
    
    # OCR服务配置
    OCR_API_KEY: str = ""
    OCR_API_URL: str = ""
    
    # 通知服务配置
    FIREBASE_SERVER_KEY: str = ""

    # 蓝心大模型-70B 配置
    VIVO_AIGC_URL: str = Field(
        "https://api-ai.vivo.com.cn/vivogpt/completions",
        env="VIVO_AIGC_URL",
        description="蓝心大模型-70B接口"
    )
    VIVO_APP_ID: str = Field(
        "2025961609",
        env="VIVO_APP_ID",
        description="蓝心大模型 AppID"
    )
    VIVO_APP_KEY: str = Field(
        "tHEMlCLaMJyTQUUW",
        env="VIVO_APP_KEY",
        description="蓝心大模型 AppKEY"
    )
    
    # AI 请求超时时间（秒）
    AI_API_TIMEOUT: float = Field(
        30.0,
        env="AI_API_TIMEOUT",
        description="调用 AIGC 接口时的超时时间（秒）"
    )

    # AI 任务分解接口及密钥配置
    AI_TASK_BREAKDOWN_URL: AnyHttpUrl = Field(
        "https://aigc.vivo.com.cn/api/v1/completions",
        env="AI_TASK_BREAKDOWN_URL",
        description="AI 任务分解接口 URL"
    )
    AI_API_KEY: str = Field(
        "tHEMlCLaMJyTQUUW",
        env="AI_API_KEY",
        description="AI 服务 API Key"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings() 