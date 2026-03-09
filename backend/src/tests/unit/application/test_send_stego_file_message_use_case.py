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
from domain.enums.stego_type import StegoType
from domain.enums.chat_message_type import ChatMessageType
from domain.enums.chat_message_status import ChatMessageStatus
from domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
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


def test_send_stego_file_message_success():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        sender = create_user(user_service, "sender@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=sender.id,
            user_b_id=recipient.id,
        )

        create_stego_file_use_case = CreateStegoFileUseCase(
            file_repo=file_repo,
            storage=LocalStorage(base_path=TEST_UPLOADS_PATH),
            stego_service=StegoDispatcher(),
        )

        use_case = SendStegoFileMessageUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
            create_stego_file_use_case=create_stego_file_use_case,
        )

        wav_bytes = generate_test_wav()

        result = asyncio.run(
            use_case.execute(
                conversation_id=conversation.id,
                sender_id=sender.id,
                original_filename="sample.wav",
                stego_type=StegoType.AUDIO,
                secret_data="hidden secret",
                file_bytes=wav_bytes,
                caption="listen to this",
            )
        )

        message = result["message"]
        db_file = result["file"]

        assert result["conversation"].id == conversation.id

        assert db_file.id is not None
        assert db_file.owner_id == sender.id
        assert db_file.filename.endswith("_sample.wav")

        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.sender_id == sender.id
        assert message.message_type == ChatMessageType.STEGO_FILE.value
        assert message.file_id == db_file.id
        assert message.stego_type == StegoType.AUDIO.value
        assert message.text_content == "listen to this"
        assert message.status == ChatMessageStatus.SENT.value

        latest_version = file_repo.get_latest_version(db_file.id)
        assert latest_version is not None
        assert latest_version.file_path.endswith(db_file.filename)
    finally:
        session.close()


def test_send_stego_file_message_conversation_not_found():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        sender = create_user(user_service, "sender@example.com")

        create_stego_file_use_case = CreateStegoFileUseCase(
            file_repo=file_repo,
            storage=LocalStorage(base_path=TEST_UPLOADS_PATH),
            stego_service=StegoDispatcher(),
        )

        use_case = SendStegoFileMessageUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
            create_stego_file_use_case=create_stego_file_use_case,
        )

        wav_bytes = generate_test_wav()

        with pytest.raises(ConversationNotFoundError):
            asyncio.run(
                use_case.execute(
                    conversation_id=9999,
                    sender_id=sender.id,
                    original_filename="sample.wav",
                    stego_type=StegoType.AUDIO,
                    secret_data="hidden secret",
                    file_bytes=wav_bytes,
                    caption=None,
                )
            )
    finally:
        session.close()


def test_send_stego_file_message_access_denied_for_non_participant():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        user_a = create_user(user_service, "a@example.com")
        user_b = create_user(user_service, "b@example.com")
        outsider = create_user(user_service, "outsider@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=user_a.id,
            user_b_id=user_b.id,
        )

        create_stego_file_use_case = CreateStegoFileUseCase(
            file_repo=file_repo,
            storage=LocalStorage(base_path=TEST_UPLOADS_PATH),
            stego_service=StegoDispatcher(),
        )

        use_case = SendStegoFileMessageUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
            create_stego_file_use_case=create_stego_file_use_case,
        )

        wav_bytes = generate_test_wav()

        with pytest.raises(ConversationAccessDeniedError):
            asyncio.run(
                use_case.execute(
                    conversation_id=conversation.id,
                    sender_id=outsider.id,
                    original_filename="sample.wav",
                    stego_type=StegoType.AUDIO,
                    secret_data="hidden secret",
                    file_bytes=wav_bytes,
                    caption="not allowed",
                )
            )
    finally:
        session.close()
