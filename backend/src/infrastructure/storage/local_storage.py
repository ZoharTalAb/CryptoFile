import os
from domain.interfaces.storage_interface import StorageInterface


class LocalStorage(StorageInterface):
    def __init__(self, base_path: str | None = None):
        self.base_path = base_path or "/app/uploads"
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, file_bytes: bytes, filename: str) -> str:
        file_path = os.path.join(self.base_path, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path

    def get_path(self, filename: str) -> str:
        return os.path.join(self.base_path, filename)
