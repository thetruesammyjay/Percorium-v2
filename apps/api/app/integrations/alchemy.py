from dataclasses import dataclass
from typing import Any

import httpx

from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.core.validators import require_solana_address, require_solana_signature
from app.integrations.http import post_json


@dataclass(frozen=True)
class TokenBalance:
    mint: str
    raw_amount: str
    decimals: int


class AlchemySolanaClient:
    name = "alchemy"

    def __init__(self, rpc_url: str | None, client: httpx.AsyncClient) -> None:
        self.rpc_url = rpc_url
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.rpc_url)

    async def get_portfolio(self, wallet: str, token_program_id: str) -> tuple[str, list[TokenBalance]]:
        require_solana_address(wallet, field="wallet")
        if not self.rpc_url:
            raise IntegrationNotConfiguredError(self.name)

        native_payload = await self._rpc("getBalance", [wallet])
        native_balance = self._parse_native_balance(native_payload)

        token_payload = await self._rpc(
            "getTokenAccountsByOwner",
            [
                wallet,
                {"programId": token_program_id},
                {"encoding": "jsonParsed"},
            ],
        )
        return native_balance, self._parse_token_balances(token_payload)

    async def get_signature_status(self, signature: str) -> str | None:
        require_solana_signature(signature)
        if not self.rpc_url:
            raise IntegrationNotConfiguredError(self.name)
        payload = await self._rpc("getSignatureStatuses", [[signature]])
        if not isinstance(payload, dict) or not isinstance(payload.get("value"), list):
            raise ProviderRequestError(self.name, "Alchemy returned an invalid signature status response.")
        status = payload["value"][0] if payload["value"] else None
        if status is None:
            return None
        if not isinstance(status, dict):
            raise ProviderRequestError(self.name, "Alchemy returned an invalid signature status.")
        if status.get("err") is not None:
            return "failed"
        if status.get("confirmationStatus") in {"confirmed", "finalized"}:
            return "confirmed"
        return "submitted"

    async def _rpc(self, method: str, params: list[Any]) -> Any:
        payload = await post_json(
            self.client,
            integration=self.name,
            url=self.rpc_url or "",
            payload={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        if not isinstance(payload, dict) or payload.get("error") is not None:
            raise ProviderRequestError(self.name, f"Alchemy RPC method {method} failed.")
        return payload.get("result")

    @staticmethod
    def _parse_native_balance(payload: Any) -> str:
        if not isinstance(payload, dict) or not isinstance(payload.get("value"), int):
            raise ProviderRequestError("alchemy", "Alchemy returned an invalid native balance.")
        return str(payload["value"])

    @staticmethod
    def _parse_token_balances(payload: Any) -> list[TokenBalance]:
        if not isinstance(payload, dict) or not isinstance(payload.get("value"), list):
            raise ProviderRequestError("alchemy", "Alchemy returned an invalid token account response.")

        balances: dict[str, TokenBalance] = {}
        for account in payload["value"]:
            try:
                info = account["account"]["data"]["parsed"]["info"]
                mint = str(info["mint"])
                token_amount = info["tokenAmount"]
                amount = str(token_amount["amount"])
                decimals = int(token_amount["decimals"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ProviderRequestError("alchemy", "Alchemy returned an invalid token account.") from exc
            current = balances.get(mint)
            total = str(int(current.raw_amount) + int(amount)) if current else amount
            balances[mint] = TokenBalance(mint=mint, raw_amount=total, decimals=decimals)
        return list(balances.values())
