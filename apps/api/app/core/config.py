from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "Percorium API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "staging", "production"] = Field(
        default="development", validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT")
    )
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    docs_enabled: bool = True

    database_url: str = "sqlite+aiosqlite:///./percorium.db"
    auto_create_db: bool = Field(default=True, validation_alias=AliasChoices("DB_AUTO_CREATE", "AUTO_CREATE_DB"))
    sql_echo: bool = False
    redis_url: str | None = None

    alchemy_solana_rpc_url: str | None = None
    solana_usdc_mint: str = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    solana_wrapped_sol_mint: str = "So11111111111111111111111111111111111111112"
    solana_token_program_id: str = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    sunrise_api_url: str | None = None
    sunrise_api_key: str | None = None
    sunrise_assets_path: str = "/assets"
    sunrise_quote_path: str = "/quote"
    jupiter_api_key: str | None = None
    jupiter_api_url: str = "https://api.jup.ag"
    jupiter_trigger_create_path: str = "/trigger/v2/createOrder"
    finnhub_api_key: str | None = None
    finnhub_api_url: str = "https://finnhub.io/api/v1"
    privy_app_id: str | None = None
    privy_app_secret: str | None = None
    sns_resolver_url: str | None = None
    platform_fee_wallet: str | None = None

    platform_fee_bps: int = Field(default=50, validation_alias=AliasChoices("PERCORIUM_FEE_BPS", "PLATFORM_FEE_BPS"))
    base_enabled: bool = False
    magicblock_enabled: bool = False
    auth_required: bool = Field(default=False, validation_alias="AUTH_REQUIRED")
    http_timeout_seconds: float = Field(default=10.0, gt=0, le=60.0)
    quote_ttl_seconds: int = Field(default=30, ge=5, le=300)

    @field_validator("api_prefix")
    @classmethod
    def normalize_prefix(cls, value: str) -> str:
        if not value.startswith("/"):
            return f"/{value}"
        return value.rstrip("/") or "/"

    @field_validator("platform_fee_bps")
    @classmethod
    def validate_fee_bps(cls, value: int) -> int:
        if not 0 <= value <= 10_000:
            raise ValueError("platform_fee_bps must be between 0 and 10000")
        return value

    @model_validator(mode="after")
    def validate_runtime_safety(self) -> "Settings":
        if self.is_production and not self.auth_required:
            raise ValueError("AUTH_REQUIRED must be true in production")
        if self.is_production and self.auto_create_db:
            raise ValueError("DB_AUTO_CREATE must be false in production")
        return self

    @property
    def percorium_fee_bps(self) -> int:
        """Backward-compatible name for older service callers."""
        return self.platform_fee_bps

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
