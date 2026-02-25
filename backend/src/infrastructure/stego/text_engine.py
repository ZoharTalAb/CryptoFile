from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError
from domain.interfaces.stego_engine import StegoEngine


class TextStegoEngine(StegoEngine):
    HEADER_BITS = 32  # 4 bytes length header (32 bits)

    def embed(self, cover_bytes: bytes, encrypted_payload: bytes) -> bytes:
        # המרה מ-bytes לטקסט
        try:
            cover_text = cover_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise CorruptedPayloadError("Cover text must be valid UTF-8")

        # 1. אורך + payload
        length_header = len(encrypted_payload).to_bytes(4, "big")
        full_payload = length_header + encrypted_payload

        # 2. המרה לביטים
        payload_bits = []
        for byte in full_payload:
            for i in range(8):
                payload_bits.append((byte >> (7 - i)) & 1)

        # 3. פירוק לשורות
        lines = cover_text.splitlines()

        # 4. בדיקת קיבולת
        if len(lines) < len(payload_bits):
            raise PayloadTooLargeError()

        # 5. הטמעה
        stego_lines = []
        for i, bit in enumerate(payload_bits):
            line = lines[i].rstrip()

            if bit == 0:
                line += " "
            else:
                line += "  "

            stego_lines.append(line)

        # שאר השורות
        stego_lines.extend(lines[len(payload_bits) :])

        stego_text = "\n".join(stego_lines)

        # החזרה ל-bytes
        return stego_text.encode("utf-8")

    def extract(self, stego_bytes: bytes) -> bytes:
        # המרה מ-bytes לטקסט
        try:
            stego_text = stego_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise CorruptedPayloadError("Stego text must be valid UTF-8")

        lines = stego_text.splitlines()

        # 1. קריאת header
        if len(lines) < self.HEADER_BITS:
            raise CorruptedPayloadError()

        header_bits = []
        for i in range(self.HEADER_BITS):
            trailing_spaces = len(lines[i]) - len(lines[i].rstrip(" "))

            if trailing_spaces == 1:
                header_bits.append(0)
            elif trailing_spaces == 2:
                header_bits.append(1)
            else:
                raise CorruptedPayloadError()

        # 2. המרת header לאורך
        length_bytes = bytearray()
        for i in range(0, self.HEADER_BITS, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | header_bits[i + j]
            length_bytes.append(byte)

        payload_length = int.from_bytes(length_bytes, "big")

        # 3. בדיקת תקינות
        total_payload_bits = payload_length * 8
        if len(lines) < self.HEADER_BITS + total_payload_bits:
            raise CorruptedPayloadError()

        # 4. חילוץ ביטים
        payload_bits = []
        for i in range(self.HEADER_BITS, self.HEADER_BITS + total_payload_bits):
            trailing_spaces = len(lines[i]) - len(lines[i].rstrip(" "))

            if trailing_spaces == 1:
                payload_bits.append(0)
            elif trailing_spaces == 2:
                payload_bits.append(1)
            else:
                raise CorruptedPayloadError()

        # 5. ביטים → bytes
        payload = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload_bits[i + j]
            payload.append(byte)

        return bytes(payload)
