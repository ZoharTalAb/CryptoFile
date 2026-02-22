import pytest

from infrastructure.db.models import UserModel
from infrastructure.db.session import SessionLocal
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl

from domain.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
)

from application.users.user_service import (
    UserService,
    UserAlreadyExistsError,
)


def clear_users_table(session):
    session.query(UserModel).delete()
    session.commit()


def test_user_registration():
    session = SessionLocal()
    clear_users_table(session)

    repo = UserRepositoryImpl(session)
    service = UserService(repo)

    user = service.register(
        email="test@example.com",
        password="securepassword",
    )

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.password_hash.startswith("$2b$")


def test_duplicate_user_registration():
    session = SessionLocal()
    clear_users_table(session)

    repo = UserRepositoryImpl(session)
    service = UserService(repo)

    service.register(
        email="duplicate@example.com",
        password="pass",
    )

    with pytest.raises(UserAlreadyExistsError):
        service.register(
            email="duplicate@example.com",
            password="pass",
        )


def test_successful_login():
    session = SessionLocal()
    clear_users_table(session)

    repo = UserRepositoryImpl(session)
    service = UserService(repo)

    service.register(
        email="login@example.com",
        password="mypassword",
    )

    user = service.login(
        email="login@example.com",
        password="mypassword",
    )

    assert user.email == "login@example.com"


def test_login_wrong_password():
    session = SessionLocal()
    clear_users_table(session)

    repo = UserRepositoryImpl(session)
    service = UserService(repo)

    service.register(
        email="wrongpass@example.com",
        password="correct",
    )

    with pytest.raises(InvalidCredentialsError):
        service.login(
            email="wrongpass@example.com",
            password="incorrect",
        )


def test_login_user_not_found():
    session = SessionLocal()
    clear_users_table(session)

    repo = UserRepositoryImpl(session)
    service = UserService(repo)

    with pytest.raises(UserNotFoundError):
        service.login(
            email="doesnotexist@example.com",
            password="pass",
        )
