import os
import pytest

from domain.crypto.aes_engine import AESEngine
from domain.crypto.aes_engine import InvalidKeyLengthError, DecryptionFailedError


def test_encrypt_decrypt_roundtrip():
    engine = AESEngine()
    key = os.urandom(32)
    plaintext = b"hello world"

    encrypted = engine.encrypt(plaintext, key)
    decrypted = engine.decrypt(encrypted, key)

    assert decrypted == plaintext


def test_invalid_key_length():
    engine = AESEngine()
    key = b"short"

    with pytest.raises(InvalidKeyLengthError):
        engine.encrypt(b"data", key)


def test_tampered_ciphertext():
    engine = AESEngine()
    key = os.urandom(32)

    encrypted = engine.encrypt(b"secure", key)

    tampered = bytearray(encrypted)
    tampered[-1] ^= 1

    with pytest.raises(DecryptionFailedError):
        engine.decrypt(bytes(tampered), key)
