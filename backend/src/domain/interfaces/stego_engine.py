from abc import ABC, abstractmethod


class StegoEngine(ABC):

    @abstractmethod
    def embed(self, cover_bytes: bytes, payload: bytes) -> bytes:
        pass

    @abstractmethod
    def extract(self, stego_bytes: bytes) -> bytes:
        pass
