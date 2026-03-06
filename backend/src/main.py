from fastapi import FastAPI
from sqlalchemy import text

from presentation.routes import (
    auth_routes,
    user_routes,
    stego_routes,
    share_routes,
    file_routes,
)
from infrastructure.db.session import engine

app = FastAPI(
    title="CryptoFile API",
    description="מערכת להעברת הודעות מאובטחת באמצעות סטגנוגרפיה בתמונות, אודיו וטקסט",
    version="1.0.0",
)

# Routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(stego_routes.router)
app.include_router(share_routes.router)
app.include_router(file_routes.router)


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
        # Do not leak internal details in production health endpoint
        return {"status": "ok", "db": "down"}
