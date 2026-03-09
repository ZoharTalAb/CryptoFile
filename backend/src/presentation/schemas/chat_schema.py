from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from domain.enums.chat_message_type import ChatMessageType
from domain.enums.chat_message_status import ChatMessageStatus


class CreateConversationRequest(BaseModel):
    target_email: EmailStr


class OtherUserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    message_type: ChatMessageType
    text_content: str | None = None
    file_id: int | None = None
    stego_type: str | None = None
    status: ChatMessageStatus
    created_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    created_at: datetime
    other_user: OtherUserResponse | None = None

    class Config:
        from_attributes = True


class ConversationListItemResponse(BaseModel):
    id: int
    created_at: datetime
    other_user: OtherUserResponse | None = None
    last_message: ChatMessageResponse | None = None
    unread_count: int

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: List[ConversationListItemResponse]


class MessageListResponse(BaseModel):
    conversation_id: int
    messages: List[ChatMessageResponse]


class SendTextMessageRequest(BaseModel):
    text: str


class MarkConversationReadResponse(BaseModel):
    conversation_id: int
    updated_count: int


class ExtractChatMessageResponse(BaseModel):
    message_id: int
    file_id: int
    stego_type: str
    extracted_message: str
