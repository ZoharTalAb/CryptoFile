from domain.interfaces.stego_engine import StegoEngine


class EmbedUseCase:
    def __init__(self, key_service, aes_engine, stego_engine: StegoEngine):
        self._key_service = key_service
        self._aes_engine = aes_engine
        self._stego_engine = stego_engine

    def execute(
        self,
        cover_bytes: bytes,
        payload_bytes: bytes,
        password: bytes,
    ) -> tuple[bytes, bytes, bytes]:
        """
        Returns:
            stego_file,
            wrapped_dek,
            salt
        """

        # 1️⃣ Generate keys
        dek, wrapped_dek, salt = self._key_service.generate_file_keys(password)

        # 2️⃣ Build AAD (bind ciphertext to wrapped_dek)
        aad = wrapped_dek

        # 3️⃣ Encrypt payload with AAD
        encrypted_payload = self._aes_engine.encrypt(
            payload_bytes,
            dek,
            aad=aad,
        )

        # 4️⃣ Embed encrypted payload
        stego_file = self._stego_engine.embed(
            cover_bytes,
            encrypted_payload,
        )

        return stego_file, wrapped_dek, salt
