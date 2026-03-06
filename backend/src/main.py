import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from presentation.routes import (
    auth_routes,
    user_routes,
    stego_routes,
    share_routes,
    file_routes,
)
from infrastructure.db.session import engine

from domain.exceptions import (
    DomainError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)

from fastapi.middleware.cors import CORSMiddleware
from core.config import CORS_ORIGINS, ENVIRONMENT

logger = logging.getLogger("cryptofile")

app = FastAPI(
    title="CryptoFile API",
    description="מערכת להעברת הודעות מאובטחת באמצעות סטגנוגרפיה בתמונות, אודיו וטקסט",
    version="1.0.0",
)

# ---------------------------
# Global Exception Handlers
# ---------------------------

# CORS
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
elif ENVIRONMENT != "production":
    # Dev fallback: allow localhost only patterns (keep it simple)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(status_code=400, content={"detail": "User already exists"})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "User not found"})


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    # Business/domain rule violations
    msg = str(exc).strip() or "Domain error"
    return JSONResponse(status_code=400, content={"detail": msg})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log full traceback internally, don't leak details to the client
    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------------------------
# Routers
# ---------------------------

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(stego_routes.router)
app.include_router(share_routes.router)
app.include_router(file_routes.router)


# ---------------------------
# Basic Endpoints
# ---------------------------


@app.get("/")
async def root():
    return {"message": "Welcome to CryptoFile API - Steganography Engine is Ready!"}


@app.get("/health")
def health():
    """
    Lightweight health endpoint.
    - status: API process is up
    - db: checks DB connectivity with SELECT 1
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        logger.warning("Health check failed", extra={"component": "db"})
        return {"status": "ok", "db": "down"}
