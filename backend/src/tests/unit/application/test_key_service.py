import pytest

from application.key_management.key_service import KeyService
from domain.exceptions import InvalidPasswordError


def test_generate_and_unwrap_roundtrip():
    password = b"strong-password"

    dek, wrapped_dek, salt = KeyService.generate_file_keys(password)

    recovered_dek = KeyService.unwrap_file_key(
        password,
        wrapped_dek,
        salt,
    )

    assert recovered_dek == dek


def test_wrong_password_fails():
    password = b"correct"
    wrong_password = b"wrong"

    dek, wrapped_dek, salt = KeyService.generate_file_keys(password)

    with pytest.raises(Exception):
        KeyService.unwrap_file_key(
            wrong_password,
            wrapped_dek,
            salt,
        )


def test_empty_password_raises():
    with pytest.raises(InvalidPasswordError):
        KeyService.generate_file_keys(b"")
