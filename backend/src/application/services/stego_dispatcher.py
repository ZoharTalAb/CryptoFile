from domain.stego.image_engine import ImageStegoEngine
from domain.stego.audio_engine import AudioStegoEngine
from domain.stego.text_engine import TextStegoEngine

class StegoDispatcher:
    def __init__(self):
        # אתחול של שלושת המנועים 
        self._image_engine = ImageStegoEngine()
        self._audio_engine = AudioStegoEngine()
        self._text_engine = TextStegoEngine()

    def dispatch_embed(self, stego_type: str, file_bytes: bytes, data: bytes) -> bytes:
        """
        מקבלת סוג סטגנוגרפיה, את קובץ הכיסוי ואת המידע להחבאה, ומחזירה קובץ מוטמע.
        """
        if stego_type == "image":
            return self._image_engine.embed(file_bytes, data)
        
        elif stego_type == "audio":
            return self._audio_engine.embed(file_bytes, data)
        
        elif stego_type == "text":
            return self._text_engine.embed(file_bytes, data)
        
        else:
            # אם מישהו ניסה לשלוח סוג שלא קיים (למשל 'video') - זורקים שגיאה
            raise ValueError(f"Unsupported stego type: {stego_type}")

    def dispatch_extract(self, stego_type: str, file_bytes: bytes) -> bytes:
        """
        אותו דבר בדיוק, רק לצורך חילוץ המידע מהקובץ.
        """
        if stego_type == "image":
            return self._image_engine.extract(file_bytes)
        elif stego_type == "audio":
            return self._audio_engine.extract(file_bytes)
        elif stego_type == "text":
            return self._text_engine.extract(file_bytes)
        else:
            raise ValueError(f"Unsupported stego type: {stego_type}")