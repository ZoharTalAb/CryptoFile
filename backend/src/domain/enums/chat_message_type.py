from enum import Enum


class ChatMessageType(str, Enum):
    TEXT = "text"
    STEGO_FILE = "stego_file"
