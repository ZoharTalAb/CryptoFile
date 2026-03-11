from enum import Enum


class StegoType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    VIDEO = "video"