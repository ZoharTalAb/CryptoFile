from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete
from infrastructure.db.models import UserModel, trusted_relations
from typing import List

class TrustedRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def add_trusted_relation(self, user_id: int, trusted_user_id: int):
        """יוצר קשר אמון חדש - מאפשר למשתמש אחד לשלוח הודעות וקבצים לשני"""
        # משתמשים ב-insert פשוט על טבלת הקישור
        stmt = insert(trusted_relations).values(
            user_id=user_id, 
            trusted_user_id=trusted_user_id
        )
        self.session.execute(stmt)
        self.session.commit()

    def is_trusted(self, user_id: int, sender_id: int) -> bool:
        """בודק האם לשולח יש הרשאה (אמון) לשלוח קבצים למשתמש מסוים"""
        stmt = select(trusted_relations).where(
            (trusted_relations.c.user_id == user_id) & 
            (trusted_relations.c.trusted_user_id == sender_id)
        )
        result = self.session.execute(stmt).first()
        return result is not None

    def get_all_trusted_users(self, user_id: int) -> List[int]:
        """מחזיר רשימת מזהים (IDs) של כל המשתמשים שנתת בהם אמון"""
        stmt = select(trusted_relations.c.trusted_user_id).where(
            trusted_relations.c.user_id == user_id
        )
        results = self.session.execute(stmt).all()
        return [r[0] for r in results]

    def remove_trusted_relation(self, user_id: int, trusted_id: int):
        """מסיר קשר אמון (חסימת משתמש)"""
        stmt = delete(trusted_relations).where(
            (trusted_relations.c.user_id == user_id) & 
            (trusted_relations.c.trusted_user_id == trusted_id)
        )
        self.session.execute(stmt)
        self.session.commit()