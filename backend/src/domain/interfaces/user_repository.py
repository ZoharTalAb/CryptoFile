from abc import ABC, abstractmethod
from domain.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass
