from datetime import datetime, timezone
import bcrypt

from domain.entities.user import User
from domain.interfaces.user_repository import UserRepository
from domain.exceptions import (
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

        hashed_password = self._hash_password(password)

        user = User(
            id=None,
            email=email,
            password_hash=hashed_password,
            created_at=datetime.now(timezone.utc),
        )

        return self._user_repository.save(user)

    def get_by_email(self, email: str) -> User | None:
        return self._user_repository.get_by_email(email)

    def login(self, email: str, password: str) -> User:
        user = self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")

        if not self._verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self._user_repository.get_by_id(user_id)

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
