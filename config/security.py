from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class SecurityConfig(BaseSettings):
    """Security-related configuration for the Architect system."""

    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    API_RATE_LIMITS: Dict[str, int] = Field(default_factory=dict)
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")

    # Optional features
    API_KEYS: Dict[str, str] = Field(default_factory=dict)
    OAUTH2_CLIENT_ID: Optional[str] = Field(default=None, env="OAUTH_CLIENT_ID")
    OAUTH2_CLIENT_SECRET: Optional[str] = Field(default=None, env="OAUTH_CLIENT_SECRET")
    RBAC: Dict[str, List[str]] = Field(default_factory=dict)
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

