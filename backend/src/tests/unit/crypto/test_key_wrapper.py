import os
import pytest

from domain.crypto.key_wrapper import KeyWrapper
from domain.exceptions import (
    InvalidKeyLengthError,
    DecryptionFailedError,
    InvalidWrappedKeyError,
)


def test_wrap_and_unwrap_success():
    dek = os.urandom(32)
    kek = os.urandom(32)

    wrapped = KeyWrapper.wrap(dek, kek)
    unwrapped = KeyWrapper.unwrap(wrapped, kek)

    assert unwrapped == dek


def test_wrap_invalid_dek_length():
    with pytest.raises(InvalidKeyLengthError):
        KeyWrapper.wrap(b"short", os.urandom(32))


def test_unwrap_with_wrong_kek_fails():
    dek = os.urandom(32)
    kek = os.urandom(32)
    wrong_kek = os.urandom(32)

    wrapped = KeyWrapper.wrap(dek, kek)

    with pytest.raises(DecryptionFailedError):
        KeyWrapper.unwrap(wrapped, wrong_kek)


def test_unwrap_empty_raises():
    with pytest.raises(InvalidWrappedKeyError):
        KeyWrapper.unwrap(b"", os.urandom(32))
