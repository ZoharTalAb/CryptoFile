from enum import Enum


class StegoType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
