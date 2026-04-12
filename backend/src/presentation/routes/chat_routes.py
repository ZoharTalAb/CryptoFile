from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from presentation.dependencies import get_current_user, get_db, get_storage
from presentation.schemas.chat_schema import (
    CreateConversationRequest,
    ConversationResponse,
    ConversationListItemResponse,
    ConversationListResponse,
    MessageListResponse,
    ChatMessageResponse,
    SendTextMessageRequest,
    MarkConversationReadResponse,
    ExtractChatMessageResponse,
    OtherUserResponse,
)

from application.chat.create_or_get_conversation_use_case import (
    CreateOrGetConversationUseCase,
)
from application.chat.list_conversations_use_case import ListConversationsUseCase
from application.chat.list_messages_use_case import ListMessagesUseCase
from application.chat.send_text_message_use_case import SendTextMessageUseCase
from application.chat.send_stego_file_message_use_case import (
    SendStegoFileMessageUseCase,
)
from application.chat.mark_conversation_read_use_case import (
    MarkConversationReadUseCase,
)
from application.chat.extract_chat_message_use_case import (
    ExtractChatMessageUseCase,
)
from application.files.create_stego_file_use_case import CreateStegoFileUseCase

from domain.interfaces.storage_interface import StorageInterface
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from infrastructure.db.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)
from infrastructure.db.repositories.file_share_repository_impl import (
    FileShareRepositoryImpl,
)
from infrastructure.stego.stego_dispatcher import StegoDispatcher
from infrastructure.realtime.chat_connection_manager import chat_connection_manager

from domain.enums.stego_type import StegoType
from domain.exceptions import (
    UserNotFoundError,
    InvalidConversationParticipantError,
    ConversationNotFoundError,
    ConversationAccessDeniedError,
    MessageNotFoundError,
    FileNotFoundError,
    PayloadTooLargeError,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_or_get_conversation(
    request: CreateConversationRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepositoryImpl(db)
    conversation_repo = ConversationRepositoryImpl(db)

    use_case = CreateOrGetConversationUseCase(
        user_repo=user_repo,
        conversation_repo=conversation_repo,
    )

    try:
        result = await use_case.execute(
            current_user_id=current_user.id,
            target_email=request.target_email,
        )

        other_user = result["other_user"]
        conversation = result["conversation"]

        return ConversationResponse(
            id=conversation.id,
            created_at=conversation.created_at,
            other_user=OtherUserResponse(
                id=other_user.id,
                email=other_user.email,
            ),
        )

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidConversationParticipantError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    conversation_repo = ConversationRepositoryImpl(db)
    chat_message_repo = ChatMessageRepositoryImpl(db)

    use_case = ListConversationsUseCase(
        conversation_repo=conversation_repo,
        chat_message_repo=chat_message_repo,
    )

    results = await use_case.execute(current_user_id=current_user.id)

    conversations = []
    for item in results:
        other_user = item["other_user"]
        last_message = item["last_message"]

        conversations.append(
            ConversationListItemResponse(
                id=item["conversation"].id,
                created_at=item["conversation"].created_at,
                other_user=(
                    OtherUserResponse(
                        id=other_user.id,
                        email=other_user.email,
                    )
                    if other_user
                    else None
                ),
                last_message=(
                    ChatMessageResponse.model_validate(last_message)
                    if last_message
                    else None
                ),
                unread_count=item["unread_count"],
            )
        )

    return ConversationListResponse(conversations=conversations)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
)
async def list_messages(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    conversation_repo = ConversationRepositoryImpl(db)
    chat_message_repo = ChatMessageRepositoryImpl(db)

    use_case = ListMessagesUseCase(
        conversation_repo=conversation_repo,
        chat_message_repo=chat_message_repo,
    )

    try:
        result = await use_case.execute(
            conversation_id=conversation_id,
            current_user_id=current_user.id,
        )

        return MessageListResponse(
            conversation_id=result["conversation"].id,
            messages=[
                ChatMessageResponse.model_validate(message)
                for message in result["messages"]
            ],
        )

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/conversations/{conversation_id}/messages/text",
    response_model=ChatMessageResponse,
    status_code=201,
)
async def send_text_message(
    conversation_id: int,
    request: SendTextMessageRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    conversation_repo = ConversationRepositoryImpl(db)
    chat_message_repo = ChatMessageRepositoryImpl(db)

    use_case = SendTextMessageUseCase(
        conversation_repo=conversation_repo,
        chat_message_repo=chat_message_repo,
    )

    try:
        result = await use_case.execute(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            text=request.text,
        )

        other_participant = conversation_repo.get_other_participant(
            conversation_id=conversation_id,
            current_user_id=current_user.id,
        )

        if other_participant:
            await chat_connection_manager.send_to_user(
                other_participant.user_id,
                {
                    "event": "message_created",
                    "conversation_id": conversation_id,
                    "message": ChatMessageResponse.model_validate(
                        result["message"]
                    ).model_dump(mode="json"),
                },
            )

        return ChatMessageResponse.model_validate(result["message"])

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/conversations/{conversation_id}/messages/file",
    response_model=ChatMessageResponse,
    status_code=201,
)
async def send_stego_file_message(
    conversation_id: int,
    stego_type: StegoType = Form(..., description="image, audio, text, or video"),
    secret_data: str = Form(..., description="The secret message to embed"),
    file: UploadFile = File(...),
    caption: str | None = Form(None),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    storage: StorageInterface = Depends(get_storage),
):
    conversation_repo = ConversationRepositoryImpl(db)
    chat_message_repo = ChatMessageRepositoryImpl(db)
    file_repo = FileRepositoryImpl(db)

    create_stego_file_use_case = CreateStegoFileUseCase(
        file_repo=file_repo,
        storage=storage,
        stego_service=StegoDispatcher(),
    )

    file_share_repo = FileShareRepositoryImpl(db)

    use_case = SendStegoFileMessageUseCase(
        conversation_repo=conversation_repo,
        chat_message_repo=chat_message_repo,
        create_stego_file_use_case=create_stego_file_use_case,
        file_share_repo=file_share_repo,
    )

    try:
        file_bytes = await file.read()

        result = await use_case.execute(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            original_filename=file.filename,
            stego_type=stego_type,
            secret_data=secret_data,
            file_bytes=file_bytes,
            caption=caption,
        )

        other_participant = conversation_repo.get_other_participant(
            conversation_id=conversation_id,
            current_user_id=current_user.id,
        )

        if other_participant:
            await chat_connection_manager.send_to_user(
                other_participant.user_id,
                {
                    "event": "message_created",
                    "conversation_id": conversation_id,
                    "message": ChatMessageResponse.model_validate(
                        result["message"]
                    ).model_dump(mode="json"),
                },
            )

        return ChatMessageResponse.model_validate(result["message"])

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except PayloadTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/conversations/{conversation_id}/read",
    response_model=MarkConversationReadResponse,
)
async def mark_conversation_read(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    conversation_repo = ConversationRepositoryImpl(db)
    chat_message_repo = ChatMessageRepositoryImpl(db)

    use_case = MarkConversationReadUseCase(
        conversation_repo=conversation_repo,
        chat_message_repo=chat_message_repo,
    )

    try:
        result = await use_case.execute(
            conversation_id=conversation_id,
            current_user_id=current_user.id,
        )

        other_participant = conversation_repo.get_other_participant(
            conversation_id=conversation_id,
            current_user_id=current_user.id,
        )

        if other_participant:
            await chat_connection_manager.send_to_user(
                other_participant.user_id,
                {
                    "event": "conversation_read",
                    "conversation_id": conversation_id,
                    "reader_user_id": current_user.id,
                    "updated_count": result["updated_count"],
                },
            )

        return MarkConversationReadResponse(
            conversation_id=result["conversation"].id,
            updated_count=result["updated_count"],
        )

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/messages/{message_id}/extract",
    response_model=ExtractChatMessageResponse,
)
async def extract_chat_message(
    message_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    storage: StorageInterface = Depends(get_storage),
):
    chat_message_repo = ChatMessageRepositoryImpl(db)
    conversation_repo = ConversationRepositoryImpl(db)
    file_repo = FileRepositoryImpl(db)

    use_case = ExtractChatMessageUseCase(
        chat_message_repo=chat_message_repo,
        conversation_repo=conversation_repo,
        file_repo=file_repo,
        stego_service=StegoDispatcher(),
        storage=storage,
    )

    try:
        result = await use_case.execute(
            message_id=message_id,
            current_user_id=current_user.id,
        )

        return ExtractChatMessageResponse(
            message_id=result["message_id"],
            file_id=result["file_id"],
            stego_type=result["stego_type"],
            extracted_message=result["extracted_message"],
        )

    except MessageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
