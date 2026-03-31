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

        # Return storage key, not absolute path.
        # This keeps local/dev behavior aligned with cloud storage.
        return filename

    def get_file(self, file_key: str) -> bytes:
        file_path = self.get_path(file_key)

        with open(file_path, "rb") as f:
            return f.read()

    def get_path(self, filename: str) -> str:
        # Backward-compatible:
        # if old DB rows already contain an absolute/local path, use it directly.
        if (
            os.path.isabs(filename)
            or filename.startswith(".")
            or os.path.sep in filename
        ):
            return filename

        return os.path.join(self.base_path, filename)
