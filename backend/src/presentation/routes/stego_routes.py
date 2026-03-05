import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import FileResponse # הוספנו את זה להורדת קבצים
from infrastructure.stego.stego_dispatcher import StegoDispatcher
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError
from domain.enums.stego_type import StegoType
from infrastructure.storage.local_storage import LocalStorage

storage = LocalStorage()
router = APIRouter(prefix="/stego", tags=["Steganography"])
stego_service = StegoDispatcher()

@router.post("/embed")
async def embed_message(
    stego_type: StegoType = Form(..., description="image, audio, or text"),
    secret_data: str = Form(..., description="The message you want to hide"),
    file: UploadFile = File(...),
):
    try:
        file_bytes = await file.read()
        payload = secret_data.encode("utf-8")
        result_bytes = stego_service.dispatch_embed(stego_type, file_bytes, payload)

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        storage.save(result_bytes, unique_filename)

        media_type = {StegoType.IMAGE: "image/png", StegoType.AUDIO: "audio/wav", StegoType.TEXT: "text/plain"}.get(stego_type, "application/octet-stream")
        return Response(content=result_bytes, media_type=media_type)
    except PayloadTooLargeError:
        raise HTTPException(status_code=400, detail="The message is too large for this file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/extract")
async def extract_message(stego_type: str = Form(...), file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        extracted_bytes = stego_service.dispatch_extract(stego_type, file_bytes)
        return {
            "stego_type": stego_type,
            "extracted_message": extracted_bytes.decode("utf-8"),
        }
    except CorruptedPayloadError:
        raise HTTPException(status_code=400, detail="Could not find a valid message in this file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.get("/files")
async def list_files():
    try:
        upload_dir = storage.base_path
        if not os.path.exists(upload_dir):
            return {"total_files": 0, "files": []}
        files = os.listdir(upload_dir)
        return {"total_files": len(files), "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    נתיב שמאפשר להוריד קובץ ספציפי מתיקיית ה-uploads לפי השם שלו.
    """
    file_path = os.path.join(storage.base_path, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )