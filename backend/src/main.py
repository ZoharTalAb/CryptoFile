from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv
import os
load_dotenv()

from presentation.routes import (
    auth_routes,
    user_routes,
    stego_routes,
    share_routes,
    file_routes,
    chat_routes,
    chat_ws_routes,
)
from infrastructure.db.session import engine
from core.config import CORS_ORIGINS, ENVIRONMENT
from core.logging import logger

from domain.exceptions import (
    DomainError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)

app = FastAPI(
    title="CryptoFile API",
    description="מערכת להעברת הודעות מאובטחת באמצעות סטגנוגרפיה בתמונות, אודיו, טקסט וצ'אט בסיסי",
    version="1.0.0",
)

# ---------------------------
# CORS
# ---------------------------
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
elif ENVIRONMENT != "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---------------------------
# Global Exception Handlers
# ---------------------------


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
    msg = str(exc).strip() or "Domain error"
    logger.info(
        "DomainError path=%s method=%s detail=%s", request.url.path, request.method, msg
    )
    return JSONResponse(status_code=400, content={"detail": msg})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception path=%s method=%s", request.url.path, request.method
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
app.include_router(chat_routes.router)
app.include_router(chat_ws_routes.router)

# ---------------------------
# Basic Endpoints
# ---------------------------


@app.get("/")
async def root():
    return {
        "message": "Welcome to CryptoFile API - Steganography, File Sharing, Chat, and Realtime are Ready!"
    }


@app.get("/health")
def health():
    """
    Lightweight health endpoint.
    - status: API process is up
    - db: checks DB connectivity with SELECT 1
    Returns 200 if ok, 503 if db down.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "ok", "db": "down"})
