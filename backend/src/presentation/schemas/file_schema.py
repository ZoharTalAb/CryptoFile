from datetime import datetime
from typing import List

from pydantic import BaseModel


class EmbeddedFileResponse(BaseModel):
    file_id: int
    filename: str
    original_filename: str
    stego_type: str
    download_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractResponse(BaseModel):
    stego_type: str
    extracted_message: str


class StegoFilesResponse(BaseModel):
    total_files: int
    files: List[str]


class FileItemResponse(BaseModel):
    id: int
    filename: str
    created_at: datetime
    is_owner: bool
    download_url: str
    shared_by_email: str | None = None

    class Config:
        from_attributes = True


class FilesListResponse(BaseModel):
    owned_files: List[FileItemResponse]
    shared_with_me: List[FileItemResponse]
