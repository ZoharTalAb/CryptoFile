import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from domain.exceptions import (
    InvalidKeyLengthError,
    DecryptionFailedError,
)


class AESEngine:
    KEY_SIZE = 32  # 256-bit
    NONCE_SIZE = 12  # 96-bit for GCM (recommended)

    def encrypt(
        self,
        plaintext: bytes,
        key: bytes,
        aad: bytes | None = None,
    ) -> bytes:
        if len(key) != self.KEY_SIZE:
            raise InvalidKeyLengthError()

        nonce = os.urandom(self.NONCE_SIZE)

        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, aad)

        # We prepend nonce so it can be used during decryption
        return nonce + ciphertext

    def decrypt(
        self,
        encrypted_data: bytes,
        key: bytes,
        aad: bytes | None = None,
    ) -> bytes:
        if len(key) != self.KEY_SIZE:
            raise InvalidKeyLengthError()

        if len(encrypted_data) < self.NONCE_SIZE:
            raise DecryptionFailedError()

        nonce = encrypted_data[: self.NONCE_SIZE]
        ciphertext = encrypted_data[self.NONCE_SIZE :]

        aesgcm = AESGCM(key)

        try:
            return aesgcm.decrypt(nonce, ciphertext, aad)
        except Exception:
            # Any failure (tag mismatch, tampering, wrong key, wrong AAD)
            raise DecryptionFailedError()
