import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from domain.exceptions import (
    DomainError,
    InvalidKeyLengthError,
    DecryptionFailedError,
)


class AESEngine:
    KEY_SIZE = 32  # 256-bit
    NONCE_SIZE = 12  # 96-bit for GCM

    def encrypt(self, plaintext: bytes, key: bytes) -> bytes:
        if len(key) != self.KEY_SIZE:
            raise InvalidKeyLengthError()

        nonce = os.urandom(self.NONCE_SIZE)

        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        return nonce + ciphertext

    def decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        if len(key) != self.KEY_SIZE:
            raise InvalidKeyLengthError()

        if len(encrypted_data) < self.NONCE_SIZE:
            raise DecryptionFailedError()

        nonce = encrypted_data[: self.NONCE_SIZE]
        ciphertext = encrypted_data[self.NONCE_SIZE :]

        aesgcm = AESGCM(key)

        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception:
            raise DecryptionFailedError()
