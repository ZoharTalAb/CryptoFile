import pytest
import os

from domain.crypto.kdf_engine import KDFEngine
from domain.exceptions import (
    InvalidPasswordError,
    InvalidSaltError,
)


def test_derive_key_is_deterministic():
    password = b"secure-password"
    salt = b"1234567890abcdef"

    key1 = KDFEngine.derive_key(password, salt)
    key2 = KDFEngine.derive_key(password, salt)

    assert key1 == key2
    assert len(key1) == 32


def test_empty_password_raises():
    with pytest.raises(InvalidPasswordError):
        KDFEngine.derive_key(b"", b"1234567890abcdef")


def test_short_salt_raises():
    with pytest.raises(InvalidSaltError):
        KDFEngine.derive_key(b"password", b"short")
