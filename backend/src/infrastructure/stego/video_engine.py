import io
import cv2
import numpy as np
import tempfile
import os
from domain.interfaces.stego_engine import StegoEngine
from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError

class VideoStegoEngine(StegoEngine):
    HEADER_BITS = 32

    def embed(self, video_bytes: bytes, encrypted_payload: bytes) -> bytes:
        # יצירת קובץ זמני כי OpenCV עובד עם נתיבים ולא עם Bytes ישירות
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_in:
            temp_in.write(video_bytes)
            temp_in_path = temp_in.name

        cap = cv2.VideoCapture(temp_in_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # שימוש בפורמט 'mp4v' או 'HFYU' (Lossless) כדי שהדחיסה לא תהרוס את המידע
        fourcc = cv2.VideoWriter_fourcc(*'HFYU') 
        temp_out_path = temp_in_path.replace(".mp4", "_out.avi")
        out = cv2.VideoWriter(temp_out_path, fourcc, fps, (width, height))

        # הכנת המידע להטמנה (כמו בתמונה)
        length_header = len(encrypted_payload).to_bytes(4, "big")
        full_payload = length_header + encrypted_payload
        payload_bits = []
        for byte in full_payload:
            for i in range(8):
                payload_bits.append((byte >> (7 - i)) & 1)

        bit_idx = 0
        total_bits = len(payload_bits)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if bit_idx < total_bits:
                # הפיכת הפריים ל-flat כדי להטמיע ביטים
                flat_frame = frame.flatten()
                
                # הטמנה בפריימים (LSB)
                available_space = len(flat_frame)
                bits_to_embed = min(total_bits - bit_idx, available_space)
                
                for i in range(bits_to_embed):
                    flat_frame[i] = (flat_frame[i] & 0xFE) | payload_bits[bit_idx]
                    bit_idx += 1
                
                frame = flat_frame.reshape(frame.shape)

            out.write(frame)

        cap.release()
        out.release()

        if bit_idx < total_bits:
            os.remove(temp_in_path)
            os.remove(temp_out_path)
            raise PayloadTooLargeError()

        with open(temp_out_path, "rb") as f:
            result = f.read()

        # ניקוי קבצים זמניים
        os.remove(temp_in_path)
        os.remove(temp_out_path)
        return result

    def extract(self, video_bytes: bytes) -> bytes:
        # לוגיקת החילוץ מהפריימים (דומה מאוד ל-Image)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as temp_in:
            temp_in.write(video_bytes)
            temp_in_path = temp_in.name

        cap = cv2.VideoCapture(temp_in_path)
        all_bits = []
        
        # שליפת מספיק ביטים כדי לקרוא את ה-Header
        header_extracted = False
        payload_length = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            flat_frame = frame.flatten()
            for val in flat_frame:
                all_bits.append(val & 1)
                
                # אם אספנו מספיק ל-header, נחשב את האורך
                if not header_extracted and len(all_bits) >= self.HEADER_BITS:
                    header_bytes = bytearray()
                    for i in range(0, self.HEADER_BITS, 8):
                        byte = 0
                        for j in range(8):
                            byte = (byte << 1) | all_bits[i+j]
                        header_bytes.append(byte)
                    payload_length = int.from_bytes(header_bytes, "big")
                    header_extracted = True
            
            if header_extracted and len(all_bits) >= self.HEADER_BITS + (payload_length * 8):
                break

        cap.release()
        os.remove(temp_in_path)

        if not header_extracted or len(all_bits) < self.HEADER_BITS + (payload_length * 8):
            raise CorruptedPayloadError()

        # המרה חזרה ל-Bytes
        actual_payload_bits = all_bits[self.HEADER_BITS : self.HEADER_BITS + (payload_length * 8)]
        extracted_payload = bytearray()
        for i in range(0, len(actual_payload_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | actual_payload_bits[i+j]
            extracted_payload.append(byte)

        return bytes(extracted_payload)