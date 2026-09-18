from fastapi import APIRouter

from app.api import (
    assets,
    baskets,
    gifts,
    health,
    identity,
    launches,
    market,
    mcp,
    news,
    orders,
    portfolio,
    quotes,
    social,
    trades,
    watchlist,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["quotes"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(baskets.router, prefix="/baskets", tags=["baskets"])
api_router.include_router(gifts.router, prefix="/gifts", tags=["gifts"])
api_router.include_router(identity.router, prefix="/identity", tags=["identity"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(launches.router, prefix="/launches", tags=["launches"])
