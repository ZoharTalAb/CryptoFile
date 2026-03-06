from sqlalchemy.orm import Session
from infrastructure.db.models import MessageModel

class MessageRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def save_message(self, sender_id: int, receiver_id: int, content_encrypted: bytes):
        db_msg = MessageModel(
            sender_id=sender_id, 
            receiver_id=receiver_id, 
            content_encrypted=content_encrypted
        )
        self.session.add(db_msg)
        self.session.commit()
        self.session.refresh(db_msg)
        return db_msg