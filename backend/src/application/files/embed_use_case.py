from domain.exceptions import DomainError


class EmbedUseCase:
    def __init__(self, key_service, aes_engine, stego_engine):
        self._key_service = key_service
        self._aes_engine = aes_engine
        self._stego_engine = stego_engine

    def execute(
        self,
        audio_bytes: bytes,
        payload_bytes: bytes,
        password: bytes,
    ) -> tuple[bytes, bytes, bytes]:
        """
        Returns:
            stego_audio,
            wrapped_dek,
            salt
        """

        # 1️⃣ Generate keys
        dek, wrapped_dek, salt = self._key_service.generate_file_keys(password)

        # 2️⃣ Encrypt payload
        encrypted_payload = self._aes_engine.encrypt(payload_bytes, dek)

        # 3️⃣ Embed encrypted payload into audio
        stego_audio = self._stego_engine.embed(audio_bytes, encrypted_payload)

        return stego_audio, wrapped_dek, salt
