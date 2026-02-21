import os

from domain.crypto.kdf_engine import KDFEngine
from domain.crypto.key_wrapper import KeyWrapper
from domain.exceptions import InvalidPasswordError


class KeyService:
    SALT_SIZE = 16  # 128-bit salt
    DEK_SIZE = 32  # AES-256

    @staticmethod
    def generate_file_keys(password: bytes) -> tuple[bytes, bytes, bytes]:
        if not password:
            raise InvalidPasswordError("Password cannot be empty")

        salt = os.urandom(KeyService.SALT_SIZE)
        kek = KDFEngine.derive_key(password, salt)

        dek = os.urandom(KeyService.DEK_SIZE)
        wrapped_dek = KeyWrapper.wrap(dek, kek)

        return dek, wrapped_dek, salt

    @staticmethod
    def unwrap_file_key(
        password: bytes,
        wrapped_dek: bytes,
        salt: bytes,
    ) -> bytes:
        if not password:
            raise InvalidPasswordError("Password cannot be empty")

        kek = KDFEngine.derive_key(password, salt)
        dek = KeyWrapper.unwrap(wrapped_dek, kek)

        return dek
