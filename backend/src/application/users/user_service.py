from datetime import datetime, timezone

from domain.entities.user import User
from domain.interfaces.user_repository import UserRepository
from domain.exceptions import (
    DomainError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)


class UserService:

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def register(self, email: str, password: str) -> User:
        if not email or not password:
            raise ValueError("Email and password are required")

        existing_user = self._user_repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        user = User(
            id=None,
            email=email,
            password_hash=password,
            created_at=datetime.now(timezone.utc),
        )

        return self._user_repository.save(user)

    def get_by_email(self, email: str) -> User | None:
        return self._user_repository.get_by_email(email)

    def login(self, email: str, password: str) -> User:
        user = self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")

        is_valid = self._user_repository.verify_password(email, password)
        if not is_valid:
            raise InvalidCredentialsError("Invalid credentials")

        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self._user_repository.get_by_id(user_id)
