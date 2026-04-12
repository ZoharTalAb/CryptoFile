from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def save(self, file_bytes: bytes, filename: str) -> str:
        """
        Persist file bytes and return a storage key.
        """
        raise NotImplementedError

    @abstractmethod
    def get_file(self, file_key: str) -> bytes:
        """
        Read file bytes by storage key.
        """
        raise NotImplementedError
