from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from application.services.stego_dispatcher import StegoDispatcher
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError

router = APIRouter(prefix="/stego", tags=["Steganography"])

# אתחול הדיספאצ'ר - המרכזנית שמתקשרת עם המנוע שכתבת
stego_service = StegoDispatcher()

@router.post("/embed")
async def embed_message(
    stego_type: str = Form(..., description="image, audio, or text"),
    secret_data: str = Form(..., description="The message you want to hide"),
    file: UploadFile = File(...)
):
    """
    נתיב שמקבל קובץ והודעה, ומחזיר את הקובץ עם ההודעה המוחבאת בתוכו.
    """
    try:
        # 1. קריאת הבתים של הקובץ שהועלה
        file_bytes = await file.read()
        
        # 2. המרת ההודעה ל-bytes (כי המנוע שלך עובד עם bytes)
        payload = secret_data.encode("utf-8")

        # 3. שימוש בדיספאצ'ר כדי להפעיל את המנוע המתאים (כמו ה-ImageEngine שלך)
        result_bytes = stego_service.dispatch_embed(stego_type, file_bytes, payload)

        # 4. החזרת הקובץ החדש למשתמש
        media_type = "image/png" if stego_type == "image" else "audio/wav"
        return Response(content=result_bytes, media_type=media_type)

    except PayloadTooLargeError:
        raise HTTPException(status_code=400, detail="The message is too large for this file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/extract")
async def extract_message(
    stego_type: str = Form(...),
    file: UploadFile = File(...)
):
    """
    נתיב שמקבל קובץ 'נגוע' ומחלץ ממנו את ההודעה הסודית.
    """
    try:
        file_bytes = await file.read()
        
        # חילוץ המידע בעזרת המנוע
        extracted_bytes = stego_service.dispatch_extract(stego_type, file_bytes)
        
        return {
            "stego_type": stego_type,
            "extracted_message": extracted_bytes.decode("utf-8")
        }

    except CorruptedPayloadError:
        raise HTTPException(status_code=400, detail="Could not find a valid message in this file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")