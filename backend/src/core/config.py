import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

DATABASE_URL = os.getenv("DATABASE_URL")

# Storage
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_REGION = os.getenv("R2_REGION", "auto")

# CORS
_raw_origins = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# Password policy
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
PASSWORD_MAX_LENGTH = int(os.getenv("PASSWORD_MAX_LENGTH", "64"))
PASSWORD_HISTORY_LIMIT = int(os.getenv("PASSWORD_HISTORY_LIMIT", "5"))
PASSWORD_EXPIRY_DAYS = int(os.getenv("PASSWORD_EXPIRY_DAYS", "90"))

# Login protection
LOGIN_MAX_FAILED_ATTEMPTS = int(os.getenv("LOGIN_MAX_FAILED_ATTEMPTS", "5"))
LOGIN_LOCKOUT_MINUTES = int(os.getenv("LOGIN_LOCKOUT_MINUTES", "15"))

# Email verification
EMAIL_VERIFICATION_EXP_MINUTES = int(os.getenv("EMAIL_VERIFICATION_EXP_MINUTES", "15"))
EMAIL_VERIFICATION_ENABLED = os.getenv(
    "EMAIL_VERIFICATION_ENABLED",
    "true" if ENVIRONMENT == "production" else "false",
).lower() == "true"

# Password reset
RESET_TOKEN_EXP_MINUTES = int(os.getenv("RESET_TOKEN_EXP_MINUTES", "15"))
PASSWORD_RESET_MAX_REQUESTS = int(os.getenv("PASSWORD_RESET_MAX_REQUESTS", "3"))
PASSWORD_RESET_WINDOW_MINUTES = int(os.getenv("PASSWORD_RESET_WINDOW_MINUTES", "15"))
RESET_TOKEN_DEV_RETURN = os.getenv("RESET_TOKEN_DEV_RETURN", "true").lower() == "true"

# Argon2
ARGON2_TIME_COST = int(os.getenv("ARGON2_TIME_COST", "3"))
ARGON2_MEMORY_COST = int(os.getenv("ARGON2_MEMORY_COST", "65536"))
ARGON2_PARALLELISM = int(os.getenv("ARGON2_PARALLELISM", "4"))

# Frontend
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

# Email (Resend API)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")


def _require(name: str, value: str | None):
    if not value:
        raise RuntimeError(f"{name} environment variable must be set")


# Enforce required envs in production
if ENVIRONMENT == "production":
    _require("JWT_SECRET", JWT_SECRET)
    _require("DATABASE_URL", DATABASE_URL)

    if STORAGE_BACKEND == "r2":
        _require("R2_ENDPOINT", R2_ENDPOINT)
        _require("R2_ACCESS_KEY_ID", R2_ACCESS_KEY_ID)
        _require("R2_SECRET_ACCESS_KEY", R2_SECRET_ACCESS_KEY)
        _require("R2_BUCKET", R2_BUCKET)

# In dev/test we still require JWT_SECRET for safety
_require("JWT_SECRET", JWT_SECRET)
