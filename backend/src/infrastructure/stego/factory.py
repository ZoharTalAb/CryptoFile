from domain.enums.stego_type import StegoType
from domain.interfaces.stego_engine import StegoEngine

from infrastructure.stego.audio_engine import AudioStegoEngine
from infrastructure.stego.image_engine import ImageStegoEngine
from infrastructure.stego.text_engine import TextStegoEngine


class StegoFactory:

    _engines = {
        StegoType.AUDIO: AudioStegoEngine,
        StegoType.IMAGE: ImageStegoEngine,
        StegoType.TEXT: TextStegoEngine,
    }

    @classmethod
    def get_engine(cls, stego_type: StegoType) -> StegoEngine:
        try:
            return cls._engines[stego_type]()
        except KeyError:
            raise ValueError(f"Unsupported stego type: {stego_type}")
