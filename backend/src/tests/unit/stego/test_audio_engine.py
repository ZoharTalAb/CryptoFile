import io
import wave
import pytest

from infrastructure.stego.audio_engine import AudioStegoEngine
from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError


def generate_test_wav(duration_seconds=1, sample_rate=44100):
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        num_samples = int(duration_seconds * sample_rate)
        silence = b"\x00\x00" * num_samples
        wav.writeframes(silence)

    return buffer.getvalue()


def test_embed_and_extract_roundtrip():
    engine = AudioStegoEngine()

    original_audio = generate_test_wav()
    payload = b"hello world"

    embedded_audio = engine.embed(original_audio, payload)
    extracted_payload = engine.extract(embedded_audio)

    assert extracted_payload == payload


import pytest


def test_payload_too_large():
    engine = AudioStegoEngine()

    # WAV מאוד קטן
    small_audio = generate_test_wav(duration_seconds=0.001)  # מעט samples
    large_payload = b"A" * 10000  # גדול מדי

    from domain.exceptions import PayloadTooLargeError

    with pytest.raises(PayloadTooLargeError):

        engine.embed(small_audio, large_payload)


def test_corrupted_payload_length():
    engine = AudioStegoEngine()

    original_audio = generate_test_wav()
    payload = b"hello"

    embedded = engine.embed(original_audio, payload)

    corrupted = bytearray(embedded)
    corrupted[44] ^= 1  # flip first LSB in data section

    with pytest.raises(CorruptedPayloadError):
        engine.extract(bytes(corrupted))
