from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.interfaces.user_repository import UserRepository
from infrastructure.db.models import UserModel


class UserRepositoryImpl(UserRepository):

    def __init__(self, session: Session):
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        model = self._session.query(UserModel).filter(UserModel.email == email).first()

        if not model:
            return None

        return self._to_entity(model)

    def save(self, user: User) -> User:
        # Repository לא מבצע hashing!
        model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
        )

        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.query(UserModel).filter(UserModel.id == user_id).first()

        if not model:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
        )
