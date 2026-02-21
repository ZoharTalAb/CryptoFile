from application.files.embed_use_case import EmbedUseCase
from application.files.extract_use_case import ExtractUseCase
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


def test_full_encrypt_embed_extract_decrypt_flow():
    key_service = KeyService()
    aes_engine = AESEngine()
    stego_engine = AudioStegoEngine()

    embed_use_case = EmbedUseCase(
        key_service,
        aes_engine,
        stego_engine,
    )

    extract_use_case = ExtractUseCase(
        key_service,
        aes_engine,
        stego_engine,
    )

    original_audio = generate_test_wav()
    payload = b"super-secret"
    password = b"very-strong-password"

    stego_audio, wrapped_dek, salt = embed_use_case.execute(
        original_audio,
        payload,
        password,
    )

    recovered_payload = extract_use_case.execute(
        stego_audio,
        password,
        wrapped_dek,
        salt,
    )

    assert recovered_payload == payload
