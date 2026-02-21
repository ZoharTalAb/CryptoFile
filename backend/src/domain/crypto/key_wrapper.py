from domain.crypto.aes_engine import AESEngine
from domain.exceptions import (
    InvalidKeyLengthError,
    DecryptionFailedError,
    InvalidWrappedKeyError,
)


class KeyWrapper:
    """
    Wraps and unwraps DEKs using KEK (AES-256-GCM).
    Pure domain logic.
    """

    DEK_LENGTH = 32  # AES-256

    @staticmethod
    def wrap(dek: bytes, kek: bytes) -> bytes:
        if not dek or len(dek) != KeyWrapper.DEK_LENGTH:
            raise InvalidKeyLengthError("DEK must be 32 bytes")

        engine = AESEngine()
        return engine.encrypt(dek, kek)

    @staticmethod
    def unwrap(wrapped_dek: bytes, kek: bytes) -> bytes:
        if not wrapped_dek:
            raise InvalidWrappedKeyError("Wrapped key cannot be empty")

        try:
            engine = AESEngine()
            dek = engine.decrypt(wrapped_dek, kek)
        except DecryptionFailedError:
            raise DecryptionFailedError("Failed to unwrap DEK")

        if len(dek) != KeyWrapper.DEK_LENGTH:
            raise InvalidKeyLengthError("Unwrapped DEK is invalid length")

        return dek
