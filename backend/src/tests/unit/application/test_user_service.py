import pytest

from infrastructure.db.models import UserModel
from infrastructure.db.session import SessionLocal
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl

from domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)

from application.users.user_service import UserService
from tests.conftest import TEST_PASSWORD


def clear_users_table(session):
    session.query(UserModel).delete()
    session.commit()


def test_user_registration():
    session = SessionLocal()
    try:
        clear_users_table(session)

        repo = UserRepositoryImpl(session)
        service = UserService(repo)

        user = service.register(
            email="test@example.com",
            password=TEST_PASSWORD,
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash.startswith("$argon2id$")
    finally:
        session.close()


def test_duplicate_user_registration():
    session = SessionLocal()
    try:
        clear_users_table(session)

        repo = UserRepositoryImpl(session)
        service = UserService(repo)

        service.register(
            email="duplicate@example.com",
            password=TEST_PASSWORD,
        )

        with pytest.raises(UserAlreadyExistsError):
            service.register(
                email="duplicate@example.com",
                password=TEST_PASSWORD,
            )
    finally:
        session.close()


def test_successful_login():
    session = SessionLocal()
    try:
        clear_users_table(session)

        repo = UserRepositoryImpl(session)
        service = UserService(repo)

        service.register(
            email="login@example.com",
            password=TEST_PASSWORD,
        )

        user = service.login(
            email="login@example.com",
            password=TEST_PASSWORD,
        )

        assert user.email == "login@example.com"
    finally:
        session.close()


def test_login_wrong_password():
    session = SessionLocal()
    try:
        clear_users_table(session)

        repo = UserRepositoryImpl(session)
        service = UserService(repo)

        service.register(
            email="wrongpass@example.com",
            password=TEST_PASSWORD,
        )

        with pytest.raises(InvalidCredentialsError):
            service.login(
                email="wrongpass@example.com",
                password="WrongPassword999",
            )
    finally:
        session.close()


def test_login_user_not_found():
    session = SessionLocal()
    try:
        clear_users_table(session)

        repo = UserRepositoryImpl(session)
        service = UserService(repo)

        with pytest.raises(InvalidCredentialsError):
            service.login(
                email="doesnotexist@example.com",
                password=TEST_PASSWORD,
            )
    finally:
        session.close()
