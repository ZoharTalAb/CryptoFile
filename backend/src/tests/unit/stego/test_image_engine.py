import pytest
import io
from PIL import Image
from domain.stego.image_engine import ImageStegoEngine

def test_image_stego_embed_and_extract():
    # אתחול המנוע
    engine = ImageStegoEngine()
    
    # 1. יצירת תמונת מקור לבדיקה (ריבוע כחול 50x50)
    img = Image.new('RGB', (50, 50), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    image_bytes = img_byte_arr.getvalue()

    # 2. ההודעה שאנחנו רוצים להחביא
    secret_message = b"Top Secret 2026"

    # 3. הרצת ההטמעה
    stego_bytes = engine.embed(image_bytes, secret_message)
    
    # 4. הרצת החילוץ
    extracted_message = engine.extract(stego_bytes)

    # 5. הבדיקה (Assertion) - האם מה שיצא זה מה שנכנס?
    assert extracted_message == secret_message
    print("\n✅ המנוע עבר את הבדיקה בהצלחה!")