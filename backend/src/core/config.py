import os

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60  # <-- השם הזה חייב להיות תואם ל-jwt_service

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable must be set")
