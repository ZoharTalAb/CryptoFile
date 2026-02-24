import io
import numpy as np
from PIL import Image
from domain.exceptions import (
    CorruptedPayloadError,
    PayloadTooLargeError,
)

class ImageStegoEngine:
    HEADER_BITS = 32  # 4 bytes שמציינים את אורך ההודעה

    def embed(self, image_bytes: bytes, encrypted_payload: bytes) -> bytes:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        pixels = np.array(img)
        
        flat_pixels = pixels.flatten().astype(np.uint16) 
        
        length_header = len(encrypted_payload).to_bytes(4, "big")
        full_payload = length_header + encrypted_payload
        
        if len(full_payload) * 8 > len(flat_pixels):
            raise PayloadTooLargeError()

        payload_bits = []
        for byte in full_payload:
            for i in range(8):
                payload_bits.append((byte >> (7 - i)) & 1)

        # הזרקת הביטים ל-LSB (הביט הכי פחות משמעותי)
        for i, bit in enumerate(payload_bits):
            flat_pixels[i] = (flat_pixels[i] & 0xFE) | bit

        # החזרה לצורה המקורית של התמונה
        new_pixels = flat_pixels.reshape(pixels.shape).astype(np.uint8)
        new_img = Image.fromarray(new_pixels)
        
        output_buffer = io.BytesIO()
        new_img.save(output_buffer, format="PNG") # PNG שומר על הביטים (Lossless)
        return output_buffer.getvalue()

    def extract(self, image_bytes: bytes) -> bytes:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        flat_pixels = np.array(img).flatten()

        if len(flat_pixels) < self.HEADER_BITS:
            raise CorruptedPayloadError()

        # חילוץ האורך (32 ביטים ראשונים)
        header_bits = []
        for i in range(self.HEADER_BITS):
            header_bits.append(flat_pixels[i] & 1)

        length_bytes = bytearray()
        for i in range(0, self.HEADER_BITS, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | header_bits[i + j]
            length_bytes.append(byte)

        payload_length = int.from_bytes(length_bytes, "big")

        # בדיקת תקינות בסיסית של האורך
        if self.HEADER_BITS + (payload_length * 8) > len(flat_pixels):
            raise CorruptedPayloadError()

        # חילוץ תוכן ההודעה
        payload_bits = []
        start_index = self.HEADER_BITS
        end_index = self.HEADER_BITS + (payload_length * 8)
        
        for i in range(start_index, end_index):
            payload_bits.append(flat_pixels[i] & 1)

        # המרת הביטים חזרה ל-Bytes
        extracted_payload = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload_bits[i + j]
            extracted_payload.append(byte)

        return bytes(extracted_payload)