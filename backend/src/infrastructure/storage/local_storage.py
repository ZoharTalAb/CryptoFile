import os
from domain.interfaces.storage_interface import StorageInterface

class LocalStorage(StorageInterface):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        # יצירת תיקיית ה-uploads בשרת אם היא לא קיימת
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def save(self, file_bytes: bytes, filename: str) -> str:
        file_path = os.path.join(self.base_path, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path

    def get_path(self, filename: str) -> str:
        return os.path.join(self.base_path, filename)