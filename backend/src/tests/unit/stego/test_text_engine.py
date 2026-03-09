import pytest

from infrastructure.stego.text_engine import TextStegoEngine
from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError


def build_cover_text(char_count: int) -> bytes:
    return ("A" * char_count).encode("utf-8")


def strip_zero_width_chars(text: str) -> str:
    return (
        text.replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u2060", "")
    )


def test_text_engine_roundtrip():
    engine = TextStegoEngine()
    payload = b"secret text message"

    bits_needed = 32 + len(payload) * 8
    pairs_needed = bits_needed // 2
    cover = build_cover_text(pairs_needed + 20)

    stego = engine.embed(cover, payload)
    extracted = engine.extract(stego)

    assert extracted == payload


def test_text_engine_payload_too_large():
    engine = TextStegoEngine()
    payload = b"A" * 50  # 400 bits + 32 header = 432 bits => 216 visible chars needed
    cover = build_cover_text(100)

    with pytest.raises(PayloadTooLargeError):
        engine.embed(cover, payload)


def test_text_engine_extract_corrupted_payload_missing_header():
    engine = TextStegoEngine()
    corrupted = b"plain visible text only"

    with pytest.raises(CorruptedPayloadError):
        engine.extract(corrupted)


def test_text_engine_short_payload_works_with_reasonable_cover():
    engine = TextStegoEngine()
    payload = b"hi"  # 16 bits + 32 header = 48 bits => 24 visible chars needed
    cover = build_cover_text(40)

    stego = engine.embed(cover, payload)
    extracted = engine.extract(stego)

    assert extracted == payload


def test_text_engine_preserves_visible_text():
    engine = TextStegoEngine()
    payload = b"ok"
    cover_text = "Hello world " * 10
    cover = cover_text.encode("utf-8")

    stego = engine.embed(cover, payload)
    visible = strip_zero_width_chars(stego.decode("utf-8"))

    assert visible == cover_text


def test_text_engine_empty_payload_roundtrip():
    engine = TextStegoEngine()
    payload = b""
    cover = build_cover_text(16)  # 32 header bits => 16 visible chars needed

    stego = engine.embed(cover, payload)
    extracted = engine.extract(stego)

    assert extracted == b""


def test_text_engine_invalid_utf8_cover_fails():
    engine = TextStegoEngine()

    with pytest.raises(CorruptedPayloadError):
        engine.embed(b"\xff\xfe\xfd", b"hi")


def test_text_engine_invalid_utf8_stego_fails():
    engine = TextStegoEngine()

    with pytest.raises(CorruptedPayloadError):
        engine.extract(b"\xff\xfe\xfd")
