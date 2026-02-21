from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from domain.exceptions import (
    InvalidSaltError,
    InvalidPasswordError,
)


class KDFEngine:
    """
    Derives a 32-byte KEK from a password using PBKDF2-HMAC-SHA256.
    Pure domain logic.
    """

    KEY_LENGTH = 32  # AES-256
    ITERATIONS = 200_000  # Secure baseline

    @staticmethod
    def derive_key(password: bytes, salt: bytes) -> bytes:
        if not password:
            raise InvalidPasswordError("Password cannot be empty")

        if not salt or len(salt) < 16:
            raise InvalidSaltError("Salt must be at least 16 bytes")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KDFEngine.KEY_LENGTH,
            salt=salt,
            iterations=KDFEngine.ITERATIONS,
            backend=default_backend(),
        )

        return kdf.derive(password)
