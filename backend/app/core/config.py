from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://finanzas:finanzas_dev@localhost:5432/finanzas"
    jwt_secret: str = "dev_secret_cambiar_en_prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_min: int = 30
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173", "http://localhost:3000"]
    # Email 2FA (Gmail SMTP). Si no hay SMTP, el código se loguea (dev).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "CTD <no-reply@ctd.app>"
    twofa_ttl_min: int = 10
    twofa_max_attempts: int = 5
    twofa_cooldown_s: int = 60
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        # Sin NoDecode, pydantic-settings hace json.loads antes y revienta con "a,b".
        # Acepta JSON '["a","b"]' o coma 'a,b' (docker-compose usa coma).
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            if s.startswith("["):
                import json

                try:
                    return json.loads(s)
                except Exception:
                    pass
            return [p.strip() for p in s.split(",") if p.strip()]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
