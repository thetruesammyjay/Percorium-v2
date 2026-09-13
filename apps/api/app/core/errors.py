from collections.abc import Sequence
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    return response


def validation_details(errors: Sequence[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]} for error in errors]
