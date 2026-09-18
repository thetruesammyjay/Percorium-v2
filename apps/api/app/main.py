import logging
import re
import time
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import app_error_handler, validation_details
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.db.session import dispose_engine, initialize_database

settings = get_settings()
logger = logging.getLogger("percorium.api")
_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(settings.http_timeout_seconds),
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        follow_redirects=True,
        # Railway has no proxy requirement. Keeping this false by default also
        # prevents a local HTTP(S)_PROXY from intercepting provider requests.
        trust_env=settings.http_trust_env,
    )
    await initialize_database(settings)
    try:
        yield
    finally:
        await app.state.http_client.aclose()
        await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Solana-first API for tokenized-stock discovery, trading, baskets, gifts, and social features.",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID", "X-Wallet-Address"],
    expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    candidate = request.headers.get("X-Request-ID", "")
    request_id = candidate if _REQUEST_ID.fullmatch(candidate) else str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_request_error request_id=%s path=%s", request_id, request.url.path)
        raise
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    logger.info(
        "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    return await app_error_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    response = JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "The request could not be validated.",
                "details": validation_details(exc.errors()),
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    return response


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unexpected_error request_id=%s", getattr(request.state, "request_id", None), exc_info=exc)
    request_id = getattr(request.state, "request_id", "")
    response = JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred.",
                "details": {},
                "request_id": request_id,
            }
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs", "health": "/api/health"}


app.include_router(api_router, prefix=settings.api_prefix)
