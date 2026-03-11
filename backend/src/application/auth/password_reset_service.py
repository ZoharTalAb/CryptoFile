import hashlib
import secrets


class PasswordResetService:

    def generate_raw_token(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
