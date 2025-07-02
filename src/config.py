"""
系統配置管理
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """系統設定"""
    
    # OpenAI 設定
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("GPT-4omini", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.3, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(1000, env="OPENAI_MAX_TOKENS")
    
    # 資料庫設定
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    
    # 系統設定
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # API 設定
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_workers: int = Field(1, env="API_WORKERS")
    
    # 安全設定
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_origins: str = Field("*", env="ALLOWED_ORIGINS")
    
    # 效能設定
    max_concurrent_requests: int = Field(100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(30, env="REQUEST_TIMEOUT")
    
    # 監控設定
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(8001, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全域設定實例
settings = Settings()


def get_settings() -> Settings:
    """獲取設定實例"""
    return settings
