import os
import pytest

from domain.crypto.aes_engine import AESEngine
from domain.exceptions import (
    InvalidKeyLengthError,
    DecryptionFailedError,
)


def test_encrypt_decrypt_roundtrip():
    engine = AESEngine()
    key = os.urandom(32)
    data = b"hello world"

    encrypted = engine.encrypt(data, key)
    decrypted = engine.decrypt(encrypted, key)

    assert decrypted == data


def test_invalid_key_length():
    engine = AESEngine()
    key = os.urandom(16)  # wrong size
    data = b"test"

    with pytest.raises(InvalidKeyLengthError):
        engine.encrypt(data, key)


def test_decryption_with_wrong_key_fails():
    engine = AESEngine()
    key1 = os.urandom(32)
    key2 = os.urandom(32)
    data = b"secret"

    encrypted = engine.encrypt(data, key1)

    with pytest.raises(DecryptionFailedError):
        engine.decrypt(encrypted, key2)


def test_aad_mismatch_should_fail():
    engine = AESEngine()

    key = os.urandom(32)
    data = b"super secret data"

    aad_correct = b"metadata_v1"
    aad_wrong = b"metadata_v2"

    encrypted = engine.encrypt(data, key, aad=aad_correct)

    with pytest.raises(DecryptionFailedError):
        engine.decrypt(encrypted, key, aad=aad_wrong)
