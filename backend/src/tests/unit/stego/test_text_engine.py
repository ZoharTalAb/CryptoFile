import pytest
from infrastructure.stego.text_engine import TextStegoEngine
from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError


# פונקציית עזר ליצירת טקסט עם מספר שורות רצוי
def generate_test_text(lines_count=100):
    return "\n".join([f"This is cover line number {i}" for i in range(lines_count)])


def test_text_embed_and_extract_roundtrip():
    engine = TextStegoEngine()

    # טקסט מספיק ארוך → ממירים ל-bytes
    original_text = generate_test_text(lines_count=200).encode("utf-8")
    payload = b"secret text message"

    # embed + extract
    stego_bytes = engine.embed(original_text, payload)
    extracted_payload = engine.extract(stego_bytes)

    assert extracted_payload == payload


def test_text_payload_too_large():
    engine = TextStegoEngine()

    # טקסט קצר מדי → ממירים ל-bytes
    short_text = generate_test_text(lines_count=10).encode("utf-8")
    payload = b"A" * 50

    with pytest.raises(PayloadTooLargeError):
        engine.embed(short_text, payload)


def test_text_corrupted_payload():
    engine = TextStegoEngine()

    original_text = generate_test_text(lines_count=100).encode("utf-8")
    payload = b"test"

    stego_bytes = engine.embed(original_text, payload)

    # נגרום לשחיתות ע"י הסרת הרווחים מהשורה הראשונה
    lines = stego_bytes.decode("utf-8").splitlines()
    lines[0] = lines[0].rstrip()
    corrupted_bytes = "\n".join(lines).encode("utf-8")

    with pytest.raises(CorruptedPayloadError):
        engine.extract(corrupted_bytes)
