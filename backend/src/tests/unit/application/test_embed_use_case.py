import pytest

from application.files.embed_use_case import EmbedUseCase
from application.key_management.key_service import KeyService
from domain.crypto.aes_engine import AESEngine
from domain.stego.audio_engine import AudioStegoEngine


def generate_test_wav(duration_seconds=1, sample_rate=44100):
    import io
    import wave

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        num_samples = int(duration_seconds * sample_rate)
        silence = b"\x00\x00" * num_samples
        wav.writeframes(silence)

    return buffer.getvalue()


def test_embed_use_case_roundtrip():
    key_service = KeyService()
    aes_engine = AESEngine()
    stego_engine = AudioStegoEngine()

    use_case = EmbedUseCase(
        key_service,
        aes_engine,
        stego_engine,
    )

    original_audio = generate_test_wav()
    payload = b"secret-data"
    password = b"strong-password"

    stego_audio, wrapped_dek, salt = use_case.execute(
        original_audio,
        payload,
        password,
    )

    # Extract manually to validate flow
    encrypted_payload = stego_engine.extract(stego_audio)

    dek = key_service.unwrap_file_key(
        password,
        wrapped_dek,
        salt,
    )

    decrypted = aes_engine.decrypt(encrypted_payload, dek)

    assert decrypted == payload
