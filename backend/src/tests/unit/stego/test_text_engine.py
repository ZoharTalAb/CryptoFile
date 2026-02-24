import pytest
from domain.stego.text_engine import TextStegoEngine
from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError

# פונקציית עזר ליצירת טקסט עם מספר שורות רצוי
def generate_test_text(lines_count=100):
    return "\n".join([f"This is cover line number {i}" for i in range(lines_count)])

def test_text_embed_and_extract_roundtrip():
    engine = TextStegoEngine()
    
    # יוצרים טקסט מספיק ארוך (לפחות 32 שורות ל-Header + שורות להודעה)
    original_text = generate_test_text(lines_count=200)
    payload = b"secret text message"

    # מבצעים הטמעה ואז חילוץ
    stego_text = engine.embed(original_text, payload)
    extracted_payload = engine.extract(stego_text)

    # הבדיקה המרכזית: מה שהכנסנו חייב להיות מה שהוצאנו
    assert extracted_payload == payload

def test_text_payload_too_large():
    engine = TextStegoEngine()
    
    # טקסט קצר מדי (רק 10 שורות, לא מספיק אפילו ל-32 ביטים של ה-Header)
    short_text = generate_test_text(lines_count=10)
    payload = b"A" * 50 

    with pytest.raises(PayloadTooLargeError):
        engine.embed(short_text, payload)

def test_text_corrupted_payload():
    engine = TextStegoEngine()
    
    original_text = generate_test_text(lines_count=100)
    payload = b"test"
    
    stego_text = engine.embed(original_text, payload)
    
    # גרימת נזק מכוון: נוריד את הרווחים מהשורה הראשונה (חלק מה-Header)
    lines = stego_text.splitlines()
    lines[0] = lines[0].rstrip() # הסרת הרווחים שהחבאנו
    corrupted_text = "\n".join(lines)

    with pytest.raises(CorruptedPayloadError):
        engine.extract(corrupted_text)