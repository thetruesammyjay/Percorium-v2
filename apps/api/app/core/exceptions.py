class AppError(Exception):
    def __init__(self, message: str, *, code: str, status_code: int, details: object | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class IntegrationNotConfiguredError(AppError):
    def __init__(self, integration: str) -> None:
        super().__init__(
            f"{integration} integration is not configured.",
            code="integration_not_configured",
            status_code=503,
            details={"integration": integration},
        )


class ProviderRequestError(AppError):
    def __init__(self, integration: str, message: str = "The upstream provider request failed.") -> None:
        super().__init__(message, code="provider_request_failed", status_code=502, details={"integration": integration})


class UnsupportedAssetError(AppError):
    def __init__(self, mint: str) -> None:
        super().__init__(
            "The requested mint is not in the approved asset allowlist.",
            code="unsupported_asset",
            status_code=422,
            details={"mint": mint},
        )


class NotFoundError(AppError):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"{resource} was not found.", code="not_found", status_code=404, details={"resource": resource}
        )


class IdempotencyConflictError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "This idempotency key was already used with a different request.",
            code="idempotency_conflict",
            status_code=409,
        )


class AuthenticationError(AppError):
    def __init__(self, message: str = "Wallet authentication is required.") -> None:
        super().__init__(message, code="authentication_required", status_code=401)
