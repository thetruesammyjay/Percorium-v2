from fastapi.testclient import TestClient

from app.main import app

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


def test_quote_returns_explicit_not_configured_state() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/quotes",
            json={
                "rail": "solana",
                "sell_mint": SOL_MINT,
                "buy_mint": USDC_MINT,
                "sell_amount": "1000000",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_configured"
    assert body["fee_bps"] == 50
    assert body["platform_fee"] == "5000"
    assert body["transaction"] is None


def test_invalid_quote_has_structured_validation_error() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/quotes",
            json={"sell_mint": SOL_MINT, "buy_mint": USDC_MINT, "sell_amount": "0"},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.headers["X-Request-ID"]


def test_protected_routes_require_a_wallet_boundary() -> None:
    with TestClient(app) as client:
        response = client.get("/api/portfolio")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"


def test_mcp_manifest_does_not_advertise_unimplemented_copy_automation() -> None:
    with TestClient(app) as client:
        response = client.get("/api/mcp/manifest")

    assert response.status_code == 200
    tools = {tool["name"]: tool for tool in response.json()["tools"]}
    assert tools["swap"]["enabled"] is True
    assert tools["copy_once"]["enabled"] is False
