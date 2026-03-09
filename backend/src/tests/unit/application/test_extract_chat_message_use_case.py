import asyncio
import pytest
from sqlalchemy import text

from infrastructure.db.session import SessionLocal
from infrastructure.db.models import (
    UserModel,
    FileModel,
    FileVersionModel,
    FileShareModel,
    FileKeyModel,
    MessageModel,
    ConversationModel,
    ConversationParticipantModel,
    ChatMessageModel,
)
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from infrastructure.db.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)
from infrastructure.storage.local_storage import LocalStorage
from infrastructure.stego.stego_dispatcher import StegoDispatcher

from application.users.user_service import UserService
from application.files.create_stego_file_use_case import CreateStegoFileUseCase
from application.chat.send_stego_file_message_use_case import (
    SendStegoFileMessageUseCase,
)
from application.chat.extract_chat_message_use_case import (
    ExtractChatMessageUseCase,
)
from domain.enums.stego_type import StegoType
from domain.exceptions import (
    MessageNotFoundError,
    ConversationAccessDeniedError,
    FileNotFoundError,
)

TEST_UPLOADS_PATH = "tests_tmp_uploads"


def clear_tables(session):
    session.query(ChatMessageModel).delete()
    session.query(ConversationParticipantModel).delete()
    session.query(ConversationModel).delete()
    session.query(FileShareModel).delete()
    session.query(FileVersionModel).delete()
    session.query(FileKeyModel).delete()
    session.query(FileModel).delete()
    session.query(MessageModel).delete()
    session.execute(text("DELETE FROM trusted_relations"))
    session.query(UserModel).delete()
    session.commit()


def create_user(service, email, password="12345678"):
    return service.register(email=email, password=password)


def generate_test_wav(duration_seconds=1, sample_rate=44100):
    import io
    import wave

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        num_samples = int(duration_seconds * sample_rate)
        silence = b"\x00\x00" * num_samples
        wav.writeframes(silence)

    return buffer.getvalue()


def create_stego_message_for_test(
    session, sender_email="sender@example.com", recipient_email="recipient@example.com"
):
    user_repo = UserRepositoryImpl(session)
    file_repo = FileRepositoryImpl(session)
    conversation_repo = ConversationRepositoryImpl(session)
    chat_message_repo = ChatMessageRepositoryImpl(session)
    user_service = UserService(user_repo)

    sender = create_user(user_service, sender_email)
    recipient = create_user(user_service, recipient_email)

    conversation = conversation_repo.create_conversation_with_participants(
        user_a_id=sender.id,
        user_b_id=recipient.id,
    )

    create_stego_file_use_case = CreateStegoFileUseCase(
        file_repo=file_repo,
        storage=LocalStorage(base_path=TEST_UPLOADS_PATH),
        stego_service=StegoDispatcher(),
    )

    send_use_case = SendStegoFileMessageUseCase(
        conversation_repo=conversation_repo,
        chat_message_repo=chat_message_repo,
        create_stego_file_use_case=create_stego_file_use_case,
    )

    wav_bytes = generate_test_wav()

    send_result = asyncio.run(
        send_use_case.execute(
            conversation_id=conversation.id,
            sender_id=sender.id,
            original_filename="sample.wav",
            stego_type=StegoType.AUDIO,
            secret_data="super secret payload",
            file_bytes=wav_bytes,
            caption="secret audio",
        )
    )

    return {
        "sender": sender,
        "recipient": recipient,
        "conversation": conversation,
        "message": send_result["message"],
    }


def test_extract_chat_message_success_for_participant():
    session = SessionLocal()
    try:
        clear_tables(session)

        data = create_stego_message_for_test(session)

        use_case = ExtractChatMessageUseCase(
            chat_message_repo=ChatMessageRepositoryImpl(session),
            conversation_repo=ConversationRepositoryImpl(session),
            file_repo=FileRepositoryImpl(session),
            stego_service=StegoDispatcher(),
        )

        result = asyncio.run(
            use_case.execute(
                message_id=data["message"].id,
                current_user_id=data["recipient"].id,
            )
        )

        assert result["message_id"] == data["message"].id
        assert result["file_id"] == data["message"].file_id
        assert result["stego_type"] == StegoType.AUDIO.value
        assert result["extracted_message"] == "super secret payload"
    finally:
        session.close()


def test_extract_chat_message_not_found():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        user_service = UserService(user_repo)
        user = create_user(user_service, "user@example.com")

        use_case = ExtractChatMessageUseCase(
            chat_message_repo=ChatMessageRepositoryImpl(session),
            conversation_repo=ConversationRepositoryImpl(session),
            file_repo=FileRepositoryImpl(session),
            stego_service=StegoDispatcher(),
        )

        with pytest.raises(MessageNotFoundError):
            asyncio.run(
                use_case.execute(
                    message_id=9999,
                    current_user_id=user.id,
                )
            )
    finally:
        session.close()


def test_extract_chat_message_access_denied_for_non_participant():
    session = SessionLocal()
    try:
        clear_tables(session)

        data = create_stego_message_for_test(session)
        user_repo = UserRepositoryImpl(session)
        user_service = UserService(user_repo)
        outsider = create_user(user_service, "outsider@example.com")

        use_case = ExtractChatMessageUseCase(
            chat_message_repo=ChatMessageRepositoryImpl(session),
            conversation_repo=ConversationRepositoryImpl(session),
            file_repo=FileRepositoryImpl(session),
            stego_service=StegoDispatcher(),
        )

        with pytest.raises(ConversationAccessDeniedError):
            asyncio.run(
                use_case.execute(
                    message_id=data["message"].id,
                    current_user_id=outsider.id,
                )
            )
    finally:
        session.close()


def test_extract_chat_message_without_stego_file_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        user_a = create_user(user_service, "a@example.com")
        user_b = create_user(user_service, "b@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=user_a.id,
            user_b_id=user_b.id,
        )

        text_message = chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=user_a.id,
            text_content="plain text only",
        )

        use_case = ExtractChatMessageUseCase(
            chat_message_repo=chat_message_repo,
            conversation_repo=conversation_repo,
            file_repo=FileRepositoryImpl(session),
            stego_service=StegoDispatcher(),
        )

        with pytest.raises(FileNotFoundError):
            asyncio.run(
                use_case.execute(
                    message_id=text_message.id,
                    current_user_id=user_b.id,
                )
            )
    finally:
        session.close()
