from domain.interfaces.stego_engine import StegoEngine
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError


class TextStegoEngine(StegoEngine):
    """
    Text steganography using zero-width Unicode characters.

    Each visible character can carry 2 bits by appending one zero-width marker:
    - U+200B -> 00
    - U+200C -> 01
    - U+200D -> 10
    - U+2060 -> 11

    Advantages:
    - Preserves visible appearance of the text
    - Good capacity: 2 bits per visible character
    - Deterministic and easy to extract

    Note:
    - If the text is passed through systems that strip zero-width characters,
      the hidden payload may be lost.
    """

    HEADER_SIZE_BITS = 32

    BIT_PAIR_TO_CHAR = {
        "00": "\u200b",  # zero width space
        "01": "\u200c",  # zero width non-joiner
        "10": "\u200d",  # zero width joiner
        "11": "\u2060",  # word joiner
    }

    CHAR_TO_BIT_PAIR = {value: key for key, value in BIT_PAIR_TO_CHAR.items()}

    def _bytes_to_bits(self, data: bytes) -> str:
        return "".join(f"{byte:08b}" for byte in data)

    def _bits_to_bytes(self, bits: str) -> bytes:
        if len(bits) % 8 != 0:
            raise CorruptedPayloadError("Bit stream length is invalid")

        return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    def _chunk_bits_exact(self, bits: str, size: int = 2) -> list[str]:
        """
        Split bits into fixed-size chunks.
        The caller must ensure the bit length is compatible with the format.
        """
        if len(bits) % size != 0:
            raise CorruptedPayloadError("Bit stream length is not aligned correctly")

        return [bits[i : i + size] for i in range(0, len(bits), size)]

    def embed(self, cover_bytes: bytes, payload: bytes) -> bytes:
        try:
            cover_text = cover_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CorruptedPayloadError("Cover text is not valid UTF-8") from exc

        if not cover_text:
            raise PayloadTooLargeError("Text cover is empty")

        payload_bits = self._bytes_to_bits(payload)
        header_bits = f"{len(payload):032b}"
        full_bits = header_bits + payload_bits

        # header is 32 bits and payload is byte-aligned, so total is always divisible by 2
        bit_pairs = self._chunk_bits_exact(full_bits, 2)

        visible_char_count = len(cover_text)
        required_visible_chars = len(bit_pairs)

        if visible_char_count < required_visible_chars:
            raise PayloadTooLargeError(
                f"Text cover too small: need at least {required_visible_chars} visible characters, got {visible_char_count}"
            )

        encoded_parts: list[str] = []
        pair_index = 0

        for ch in cover_text:
            encoded_parts.append(ch)

            if pair_index < required_visible_chars:
                encoded_parts.append(self.BIT_PAIR_TO_CHAR[bit_pairs[pair_index]])
                pair_index += 1

        return "".join(encoded_parts).encode("utf-8")

    def extract(self, stego_bytes: bytes) -> bytes:
        try:
            stego_text = stego_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CorruptedPayloadError("Stego text is not valid UTF-8") from exc

        bit_pairs: list[str] = []
        i = 0
        n = len(stego_text)

        while i < n:
            ch = stego_text[i]

            # Skip stray zero-width chars that appear unexpectedly
            if ch in self.CHAR_TO_BIT_PAIR:
                i += 1
                continue

            if i + 1 < n and stego_text[i + 1] in self.CHAR_TO_BIT_PAIR:
                bit_pairs.append(self.CHAR_TO_BIT_PAIR[stego_text[i + 1]])
                i += 2
            else:
                i += 1

        bit_stream = "".join(bit_pairs)

        if len(bit_stream) < self.HEADER_SIZE_BITS:
            raise CorruptedPayloadError("Missing payload length header")

        header_bits = bit_stream[: self.HEADER_SIZE_BITS]
        payload_len = int(header_bits, 2)

        payload_bits_needed = payload_len * 8
        total_bits_needed = self.HEADER_SIZE_BITS + payload_bits_needed

        if len(bit_stream) < total_bits_needed:
            raise CorruptedPayloadError("Stego text does not contain full payload")

        payload_bits = bit_stream[self.HEADER_SIZE_BITS : total_bits_needed]
        return self._bits_to_bytes(payload_bits)
