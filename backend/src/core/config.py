import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60
