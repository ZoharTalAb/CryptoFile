from domain.interfaces.stego_engine import StegoEngine


class ExtractUseCase:
    def __init__(self, key_service, aes_engine, stego_engine: StegoEngine):
        self._key_service = key_service
        self._aes_engine = aes_engine
        self._stego_engine = stego_engine

    def execute(
        self,
        stego_bytes: bytes,
        password: bytes,
        wrapped_dek: bytes,
        salt: bytes,
    ) -> bytes:
        """
        Returns:
            decrypted payload (original plaintext bytes)
        """

        # 1️⃣ Extract encrypted payload
        encrypted_payload = self._stego_engine.extract(stego_bytes)

        # 2️⃣ Reconstruct DEK
        dek = self._key_service.unwrap_file_key(
            password,
            wrapped_dek,
            salt,
        )

        # 3️⃣ Build AAD (must match EmbedUseCase)
        aad = wrapped_dek

        # 4️⃣ Decrypt with AAD
        plaintext = self._aes_engine.decrypt(
            encrypted_payload,
            dek,
            aad=aad,
        )

        return plaintext
