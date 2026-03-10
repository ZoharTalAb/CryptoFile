from domain.enums.stego_type import StegoType

from infrastructure.stego.audio_engine import AudioStegoEngine
from infrastructure.stego.image_engine import ImageStegoEngine
from infrastructure.stego.text_engine import TextStegoEngine
from infrastructure.stego.video_engine import VideoStegoEngine


class StegoDispatcher:
    def __init__(self):
        self._image_engine = ImageStegoEngine()
        self._audio_engine = AudioStegoEngine()
        self._text_engine = TextStegoEngine()
        self._video_engine = VideoStegoEngine()

    def dispatch_embed(
        self,
        stego_type: StegoType,
        file_bytes: bytes,
        data: bytes,
    ) -> bytes:
        if stego_type == StegoType.IMAGE:
            return self._image_engine.embed(file_bytes, data)

        elif stego_type == StegoType.AUDIO:
            return self._audio_engine.embed(file_bytes, data)

        elif stego_type == StegoType.TEXT:
            return self._text_engine.embed(file_bytes, data)
        
        elif stego_type == StegoType.VIDEO:
            return self._video_engine.embed(file_bytes, data)

        else:
            raise ValueError(f"Unsupported stego type: {stego_type}")
        

    def dispatch_extract(
        self,
        stego_type: StegoType,
        file_bytes: bytes,
    ) -> bytes:
        if stego_type == StegoType.IMAGE:
            return self._image_engine.extract(file_bytes)

        elif stego_type == StegoType.AUDIO:
            return self._audio_engine.extract(file_bytes)

        elif stego_type == StegoType.TEXT:
            return self._text_engine.extract(file_bytes)
        
        elif stego_type == StegoType.VIDEO:
            return self._video_engine.extract(file_bytes)

        else:
            raise ValueError(f"Unsupported stego type: {stego_type}")
