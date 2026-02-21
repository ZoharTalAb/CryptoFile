class ExtractUseCase:
    def __init__(self, key_service, aes_engine, stego_engine):
        self._key_service = key_service
        self._aes_engine = aes_engine
        self._stego_engine = stego_engine

    def execute(
        self,
        stego_audio: bytes,
        password: bytes,
        wrapped_dek: bytes,
        salt: bytes,
    ) -> bytes:
        """
        Returns:
            decrypted payload (original plaintext bytes)
        """

        # 1️⃣ Extract encrypted payload from audio
        encrypted_payload = self._stego_engine.extract(stego_audio)

        # 2️⃣ Reconstruct DEK
        dek = self._key_service.unwrap_file_key(
            password,
            wrapped_dek,
            salt,
        )

        # 3️⃣ Decrypt
        plaintext = self._aes_engine.decrypt(encrypted_payload, dek)

        return plaintext
