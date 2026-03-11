from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from core.config import JWT_ALGORITHM, JWT_EXP_MINUTES, JWT_SECRET


class JWTService:

    @staticmethod
    def create_token(user_id: int, email: str, token_version: int = 0) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)

        payload = {
            "sub": str(user_id),
            "email": email,
            "ver": token_version,
            "exp": expire,
        }

        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
            return payload
        except JWTError:
            raise ValueError("Invalid or expired token")
