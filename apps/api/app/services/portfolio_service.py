import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.repositories import AssetRepository
from app.integrations.alchemy import AlchemySolanaClient
from app.schemas.portfolio import PortfolioResponse, PortfolioToken


class PortfolioService:
    def __init__(self, session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.settings = settings
        self.assets = AssetRepository(session)
        self.alchemy = AlchemySolanaClient(settings.alchemy_solana_rpc_url, client)

    async def get(self, wallet: str) -> PortfolioResponse:
        if not self.alchemy.configured:
            return PortfolioResponse(
                status="not_configured",
                wallet=wallet,
                native_balance_lamports="0",
                tokens=[],
                message="Configure Alchemy Solana RPC credentials before loading balances.",
            )

        native_balance, raw_tokens = await self.alchemy.get_portfolio(
            wallet,
            token_program_id=self.settings.solana_token_program_id,
        )
        allowed_assets = {asset.mint: (asset.symbol, asset.name) for asset in await self.assets.list_assets(limit=100)}
        allowed_assets.update(
            {
                self.settings.solana_usdc_mint: ("USDC", "USD Coin"),
                self.settings.solana_wrapped_sol_mint: ("SOL", "Wrapped SOL"),
            }
        )

        tokens = []
        for token in raw_tokens:
            if token.raw_amount == "0" or token.mint not in allowed_assets:
                continue
            symbol, name = allowed_assets[token.mint]
            tokens.append(
                PortfolioToken(
                    mint=token.mint,
                    symbol=symbol,
                    name=name,
                    raw_amount=token.raw_amount,
                    decimals=token.decimals,
                )
            )
        return PortfolioResponse(
            status="ready",
            wallet=wallet,
            native_balance_lamports=native_balance,
            tokens=tokens,
            message=None,
        )
