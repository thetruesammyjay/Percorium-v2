import re

from pydantic import Field, field_validator

from app.schemas.common import APIModel


class IdentityUpdate(APIModel):
    handle: str | None = Field(default=None, min_length=4, max_length=25)
    sns_name: str | None = Field(default=None, max_length=255)

    @field_validator("handle")
    @classmethod
    def normalize_handle(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.lower()
        if normalized.startswith("@"):
            normalized = normalized[1:]
        if not re.fullmatch(r"[a-z0-9_]{3,24}", normalized):
            raise ValueError("handle must use 3-24 lowercase letters, numbers, or underscores")
        return f"@{normalized}"

    @field_validator("sns_name")
    @classmethod
    def validate_sns_name(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[a-z0-9-]+\.(?:sol|sns)", value.lower()):
            raise ValueError("sns_name must be a valid .sol or .sns name")
        return value.lower() if value else None


class IdentityResponse(APIModel):
    wallet: str
    handle: str
    sns_name: str | None = None
