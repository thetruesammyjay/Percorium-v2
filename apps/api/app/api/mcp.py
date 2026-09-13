from fastapi import APIRouter

from app.schemas.mcp import MCPManifestResponse, MCPTool

router = APIRouter()


@router.get("/manifest", response_model=MCPManifestResponse)
async def manifest() -> MCPManifestResponse:
    return MCPManifestResponse(
        version="0.1",
        tools=[
            MCPTool(
                name="list_assets",
                description="List official Sunrise-listed stocks and ETFs.",
                method="GET",
                path="/api/assets",
                requires_wallet=False,
            ),
            MCPTool(
                name="quote",
                description="Prepare a short-lived quote with the Percorium fee breakdown.",
                method="POST",
                path="/api/quotes",
                requires_wallet=False,
            ),
            MCPTool(
                name="swap",
                description="Prepare a wallet-signed market trade intent.",
                method="POST",
                path="/api/trades",
            ),
            MCPTool(
                name="gift",
                description="Create a wallet-funded gift claim.",
                method="POST",
                path="/api/gifts",
            ),
            MCPTool(
                name="basket",
                description="Create a basket of official Sunrise assets.",
                method="POST",
                path="/api/baskets",
            ),
            MCPTool(
                name="balances",
                description="Read official token balances for the authenticated wallet.",
                method="GET",
                path="/api/portfolio",
            ),
            MCPTool(
                name="copy_once",
                description="Create a user-confirmed prefilled trade from a public fill.",
                method="POST",
                path="/api/social/copy-once",
                enabled=False,
            ),
        ],
    )
