"""
Configuration settings for SynapScale API
"""

import os
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SynapScale API"
    VERSION: str = "1.0.0"
    
    # Database Configuration
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "synapscale")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Configure appropriately for production
    
    # Migration settings
    MIGRATION_ENABLED: bool = True
    MIGRATION_PHASE: int = 1  # 1-4 representing current migration phase
    MIGRATION_TRACKING_ENABLED: bool = True
    MIGRATION_REDIRECT_PERCENTAGE: float = 0.0  # 0-100, percentage of legacy requests to redirect
    MIGRATION_DEPRECATION_WARNINGS: bool = True
    MIGRATION_ANALYTICS_RETENTION_DAYS: int = 90
    
    # Legacy endpoint configuration
    LEGACY_ENDPOINTS_ENABLED: bool = True
    LEGACY_DEPRECATION_DATE: str = "2024-12-31"  # ISO format date
    LEGACY_WARNING_THRESHOLD_DAYS: int = 30
    
    # Communication settings
    MIGRATION_EMAILS_ENABLED: bool = True
    MIGRATION_DASHBOARD_ENABLED: bool = True
    MIGRATION_NOTIFICATION_FREQUENCY: str = "weekly"  # daily, weekly, monthly
    
    class Config:
        env_file = ".env"


settings = Settings() 