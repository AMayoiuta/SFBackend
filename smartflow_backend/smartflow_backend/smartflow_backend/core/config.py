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
    
    # CORS设置
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:8000", "http://localhost:3000"]
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "smartflow"
    DATABASE_URI: str = ""
    
    # AI服务配置
    # AI_MODEL_API_KEY: str = ""
    # AI_MODEL_API_URL: str = ""
    
     # 添加以下AI相关配置
    AI_TASK_BREAKDOWN_URL: str = Field(
        "https://api.openai.com/v1/chat/completions", 
        env="AI_TASK_BREAKDOWN_URL"
    )
    AI_API_KEY: str = Field(..., env="AI_API_KEY")
    AI_API_TIMEOUT: int = Field(30, env="AI_API_TIMEOUT")
    
    # OCR服务配置
    OCR_API_KEY: str = ""
    OCR_API_URL: str = ""
    
    # 通知服务配置
    FIREBASE_SERVER_KEY: str = ""

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str, values: dict) -> str:
        if v:
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # 更新验证器
    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, info) -> str:
        """组装数据库连接字符串"""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=cls.POSTGRES_USER,
            password=cls.POSTGRES_PASSWORD,
            host=cls.POSTGRES_SERVER,
            path=f"{cls.POSTGRES_DB or ''}",
        )


settings = Settings() 