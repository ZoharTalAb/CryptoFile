import pytest

from infrastructure.stego.video_engine import VideoStegoEngine
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError


def generate_fake_mp4_bytes() -> bytes:
    """
    Minimal MP4-like binary for engine tests.
    Enough for our parser because it includes an 'ftyp' box and extra bytes.
    """
    return (
        b"\x00\x00\x00\x18ftypmp42"
        b"\x00\x00\x00\x00mp42isom"
        b"\x00\x00\x00\x08free" + (b"\x11\x22\x33\x44" * 512)
    )


def test_video_engine_embed_and_extract_roundtrip():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"secret video payload"

    stego_video = engine.embed(original_video, payload)
    extracted_payload = engine.extract(stego_video)

    assert extracted_payload == payload


def test_video_engine_preserves_original_prefix():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"hello"

    stego_video = engine.embed(original_video, payload)

    assert stego_video.startswith(original_video)


def test_video_engine_extract_without_stego_box_fails():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()

    with pytest.raises(CorruptedPayloadError):
        engine.extract(original_video)


def test_video_engine_invalid_video_fails_on_embed():
    engine = VideoStegoEngine()

    with pytest.raises(CorruptedPayloadError):
        engine.embed(b"not-a-real-video", b"payload")


def test_video_engine_invalid_video_fails_on_extract():
    engine = VideoStegoEngine()

    with pytest.raises(CorruptedPayloadError):
        engine.extract(b"not-a-real-video")


def test_video_engine_payload_too_large():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"A" * (engine.MAX_PAYLOAD_BYTES + 1)

    with pytest.raises(PayloadTooLargeError):
        engine.embed(original_video, payload)


def test_video_engine_empty_video_fails():
    engine = VideoStegoEngine()

    with pytest.raises(CorruptedPayloadError):
        engine.embed(b"", b"payload")


def test_video_engine_double_embed_protection():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"payload"

    stego_video = engine.embed(original_video, payload)

    with pytest.raises(CorruptedPayloadError):
        engine.embed(stego_video, b"second")


def test_video_engine_corrupted_box_length_fails():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"payload"

    stego_video = engine.embed(original_video, payload)
    corrupted = bytearray(stego_video)

    # damage the very first byte of the appended box size
    appended_box_offset = len(original_video)
    corrupted[appended_box_offset] = 0xFF

    with pytest.raises(CorruptedPayloadError):
        engine.extract(bytes(corrupted))
