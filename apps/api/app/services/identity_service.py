import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.core.validators import require_solana_address
from app.db.repositories import IdentityRepository
from app.schemas.identity import IdentityResponse, IdentityUpdate


class IdentityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.identities = IdentityRepository(session)

    async def get_or_create(self, wallet: str) -> IdentityResponse:
        require_solana_address(wallet, field="wallet")
        record = await self.identities.get(wallet)
        if record is None:
            record = await self.identities.create(wallet, await self._available_handle(wallet))
            await self.session.commit()
        return self._to_response(record)

    async def update(self, wallet: str, request: IdentityUpdate) -> IdentityResponse:
        require_solana_address(wallet, field="wallet")
        record = await self.identities.get(wallet)
        if record is None:
            record = await self.identities.create(wallet, await self._available_handle(wallet))

        if request.handle is not None and request.handle != record.handle:
            existing = await self.identities.get_by_handle(request.handle)
            if existing is not None and existing.wallet != wallet:
                raise AppError("That handle is already in use.", code="handle_taken", status_code=409)
            record.handle = request.handle

        if "sns_name" in request.model_fields_set:
            if request.sns_name is not None:
                raise AppError(
                    "SNS ownership verification is required before linking a name.",
                    code="sns_verification_required",
                    status_code=422,
                )
            record.sns_name = None

        await self.session.commit()
        return self._to_response(record)

    async def require(self, wallet: str) -> IdentityResponse:
        result = await self.identities.get(wallet)
        if result is None:
            raise NotFoundError("identity")
        return self._to_response(result)

    async def _available_handle(self, wallet: str) -> str:
        alphabet = string.ascii_lowercase + string.digits
        for _ in range(5):
            candidate = f"@user_{wallet[:8].lower()}"
            if await self.identities.get_by_handle(candidate) is None:
                return candidate
            candidate = f"@user_{''.join(secrets.choice(alphabet) for _ in range(10))}"
            if await self.identities.get_by_handle(candidate) is None:
                return candidate
        raise AppError("Could not allocate a unique handle.", code="handle_allocation_failed", status_code=503)

    @staticmethod
    def _to_response(record) -> IdentityResponse:
        return IdentityResponse(wallet=record.wallet, handle=record.handle, sns_name=record.sns_name)
