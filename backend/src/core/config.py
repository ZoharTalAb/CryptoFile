import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

# CORS - comma-separated origins (e.g. "http://localhost:5173,http://localhost:3000")
CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in CORS_ORIGINS_RAW.split(",") if o.strip()]

# Enforce secret only in production
if ENVIRONMENT == "production" and not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable must be set in production")
