from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Percorium API"
    environment: str = Field(default="development", validation_alias="APP_ENV")
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "sqlite+aiosqlite:///./percorium.db"
    redis_url: str | None = None

    alchemy_solana_rpc_url: str | None = None
    sunrise_api_url: str | None = None
    sunrise_api_key: str | None = None
    jupiter_api_key: str | None = None
    finnhub_api_key: str | None = None
    privy_app_id: str | None = None
    privy_app_secret: str | None = None

    percorium_fee_bps: int = Field(default=50, validation_alias="PERCORIUM_FEE_BPS")
    base_enabled: bool = False
    magicblock_enabled: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
