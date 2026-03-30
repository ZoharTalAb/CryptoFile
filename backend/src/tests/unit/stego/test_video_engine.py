import pytest

from infrastructure.stego.video_engine import VideoStegoEngine
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError


def generate_fake_mp4_bytes() -> bytes:
    """
    Minimal fake MP4-like payload for engine testing.
    The engine is container-safe and does not parse frames, so we only need
    stable binary content that resembles a video file.
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
    assert stego_video.startswith(original_video)


def test_video_engine_output_keeps_original_video_prefix():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"hello"

    stego_video = engine.embed(original_video, payload)

    assert stego_video[: len(original_video)] == original_video


def test_video_engine_extract_without_marker_fails():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()

    with pytest.raises(CorruptedPayloadError):
        engine.extract(original_video)


def test_video_engine_corrupted_magic_fails():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"payload"

    stego_video = engine.embed(original_video, payload)
    corrupted = stego_video[:-1] + b"X"

    with pytest.raises(CorruptedPayloadError):
        engine.extract(corrupted)


def test_video_engine_corrupted_length_fails():
    engine = VideoStegoEngine()
    original_video = generate_fake_mp4_bytes()
    payload = b"payload"

    stego_video = engine.embed(original_video, payload)

    magic_len = len(engine.MAGIC)
    corrupted = bytearray(stego_video)

    length_end = len(corrupted) - magic_len
    length_start = length_end - engine.LENGTH_SIZE

    corrupted[length_start:length_end] = (999999999).to_bytes(engine.LENGTH_SIZE, "big")

    with pytest.raises(CorruptedPayloadError):
        engine.extract(bytes(corrupted))


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
