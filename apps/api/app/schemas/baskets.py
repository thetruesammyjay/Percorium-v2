from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import APIModel


class BasketItem(APIModel):
    mint: str = Field(min_length=1, max_length=64)
    weight_bps: int = Field(ge=1, le=10_000)


class BasketCreate(APIModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=3, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    items: list[BasketItem] = Field(min_length=2, max_length=8)
    is_public: bool = True

    @field_validator("items")
    @classmethod
    def weights_must_equal_one_hundred_percent(cls, value: list[BasketItem]) -> list[BasketItem]:
        if len({item.mint for item in value}) != len(value):
            raise ValueError("each basket mint must be unique")
        if sum(item.weight_bps for item in value) != 10_000:
            raise ValueError("basket weights must total 10000 basis points")
        return value


class BasketResponse(APIModel):
    id: str
    slug: str
    name: str
    items: list[BasketItem]
    is_public: bool
    created_at: datetime


class BasketListResponse(APIModel):
    items: list[BasketResponse]
