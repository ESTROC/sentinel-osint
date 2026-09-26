from __future__ import annotations

from dataclasses import dataclass
import os


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "SentinelOSINT API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str | None = os.getenv("DATABASE_URL")
    analyst_api_key: str | None = os.getenv("ANALYST_API_KEY")
    allow_public_demo_writes: bool = _env_bool("ALLOW_PUBLIC_DEMO_WRITES", True)
    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "*")
    source_timeout_seconds: float = float(os.getenv("SOURCE_TIMEOUT_SECONDS", "12"))
    max_live_items_per_source: int = int(os.getenv("MAX_LIVE_ITEMS_PER_SOURCE", "30"))

    @property
    def allowed_origins(self) -> list[str]:
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.allowed_origins_raw.split(",") if item.strip()]


settings = Settings()
