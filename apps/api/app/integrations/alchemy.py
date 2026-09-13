"""Alchemy Solana RPC client boundary."""


class AlchemySolanaClient:
    def __init__(self, rpc_url: str | None) -> None:
        self.rpc_url = rpc_url
