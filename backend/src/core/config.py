import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

DATABASE_URL = os.getenv("DATABASE_URL")

# Uploads
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# CORS
_raw_origins = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]


def _require(name: str, value: str | None):
    if not value:
        raise RuntimeError(f"{name} environment variable must be set")


# Enforce required envs in production
if ENVIRONMENT == "production":
    _require("JWT_SECRET", JWT_SECRET)
    _require("DATABASE_URL", DATABASE_URL)

# In dev/test we still require JWT_SECRET for safety (since auth imports it)
_require("JWT_SECRET", JWT_SECRET)
