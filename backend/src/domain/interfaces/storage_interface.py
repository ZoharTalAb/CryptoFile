from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def save(self, file_bytes: bytes, filename: str) -> str:
        pass

    @abstractmethod
    def get_path(self, filename: str) -> str:
        pass