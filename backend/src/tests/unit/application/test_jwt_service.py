import os

# חייב לבוא לפני ה-import של JWTService
os.environ["JWT_SECRET"] = "test-secret-key"

import pytest
from application.auth.jwt_service import JWTService


def test_create_and_verify_token():
    token = JWTService.create_token(1, "test@example.com")

    payload = JWTService.verify_token(token)

    assert payload["sub"] == "1"
    assert payload["email"] == "test@example.com"


def test_invalid_token():
    with pytest.raises(ValueError):
        JWTService.verify_token("invalid.token.value")
