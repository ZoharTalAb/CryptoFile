from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from infrastructure.db.models import (
    ConversationModel,
    ConversationParticipantModel,
    ChatMessageModel,
)


class ConversationRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self) -> ConversationModel:
        conversation = ConversationModel()
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def add_participant(
        self, conversation_id: int, user_id: int
    ) -> ConversationParticipantModel:
        participant = ConversationParticipantModel(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        self.session.add(participant)
        self.session.commit()
        self.session.refresh(participant)
        return participant

    def create_conversation_with_participants(
        self, user_a_id: int, user_b_id: int
    ) -> ConversationModel:
        conversation = ConversationModel()
        self.session.add(conversation)
        self.session.flush()

        self.session.add_all(
            [
                ConversationParticipantModel(
                    conversation_id=conversation.id,
                    user_id=user_a_id,
                ),
                ConversationParticipantModel(
                    conversation_id=conversation.id,
                    user_id=user_b_id,
                ),
            ]
        )

        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int) -> ConversationModel | None:
        return (
            self.session.query(ConversationModel)
            .options(
                joinedload(ConversationModel.participants).joinedload(
                    ConversationParticipantModel.user
                )
            )
            .filter(ConversationModel.id == conversation_id)
            .first()
        )

    def user_is_participant(self, conversation_id: int, user_id: int) -> bool:
        participant = (
            self.session.query(ConversationParticipantModel)
            .filter(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.user_id == user_id,
            )
            .first()
        )
        return participant is not None

    def get_existing_one_to_one_conversation(
        self, user_a_id: int, user_b_id: int
    ) -> ConversationModel | None:
        conversation = (
            self.session.query(ConversationModel)
            .join(
                ConversationParticipantModel,
                ConversationParticipantModel.conversation_id == ConversationModel.id,
            )
            .filter(ConversationParticipantModel.user_id.in_([user_a_id, user_b_id]))
            .group_by(ConversationModel.id)
            .having(func.count(ConversationParticipantModel.user_id.distinct()) == 2)
            .options(
                joinedload(ConversationModel.participants).joinedload(
                    ConversationParticipantModel.user
                )
            )
            .first()
        )
        return conversation

    def list_user_conversations(self, user_id: int) -> list[ConversationModel]:
        return (
            self.session.query(ConversationModel)
            .join(
                ConversationParticipantModel,
                ConversationParticipantModel.conversation_id == ConversationModel.id,
            )
            .filter(ConversationParticipantModel.user_id == user_id)
            .options(
                joinedload(ConversationModel.participants).joinedload(
                    ConversationParticipantModel.user
                ),
                joinedload(ConversationModel.messages),
            )
            .order_by(ConversationModel.created_at.desc())
            .all()
        )

    def get_other_participant(
        self, conversation_id: int, current_user_id: int
    ) -> ConversationParticipantModel | None:
        return (
            self.session.query(ConversationParticipantModel)
            .options(joinedload(ConversationParticipantModel.user))
            .filter(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.user_id != current_user_id,
            )
            .first()
        )

    def get_last_message(self, conversation_id: int) -> ChatMessageModel | None:
        return (
            self.session.query(ChatMessageModel)
            .filter(ChatMessageModel.conversation_id == conversation_id)
            .order_by(ChatMessageModel.created_at.desc(), ChatMessageModel.id.desc())
            .first()
        )
