import io
from domain.exceptions import PayloadTooLargeError, CorruptedPayloadError

class TextStegoEngine:
    # אנחנו שומרים על 32 ביטים (4 בייטים) עבור האורך, בדיוק כמו באודיו
    HEADER_BITS = 32  

    def embed(self, cover_text: str, encrypted_payload: bytes) -> str:
        # 1. הכנת הנתונים: אורך ההודעה + ההודעה עצמה
        length_header = len(encrypted_payload).to_bytes(4, "big")
        full_payload = length_header + encrypted_payload

        # 2. הפיכת הנתונים לרשימת ביטים (0 ו-1)
        payload_bits = []
        for byte in full_payload:
            for i in range(8):
                # שליפת כל ביט בנפרד (מהגבוה לנמוך)
                payload_bits.append((byte >> (7 - i)) & 1)

        # 3. הכנת הטקסט: פירוק לשורות
        lines = cover_text.splitlines()

        # 4. בדיקת קיבולת: האם יש מספיק שורות בטקסט לכל הביטים?
        if len(lines) < len(payload_bits):
            raise PayloadTooLargeError()

        # 5. תהליך ההטמעה: הוספת רווחים בסוף כל שורה
        stego_lines = []
        for i, bit in enumerate(payload_bits):
            line = lines[i].rstrip() # ניקוי רווחים קיימים כדי למנוע טעויות
            
            if bit == 0:
                line += " "   # רווח אחד מייצג 0
            else:
                line += "  "  # שני רווחים מייצגים 1
            
            stego_lines.append(line)

        # הוספת שאר השורות המקוריות שלא השתמשנו בהן
        stego_lines.extend(lines[len(payload_bits):])

        # חיבור השורות חזרה לטקסט אחד
        return "\n".join(stego_lines)
    
    
    def extract(self, stego_text: str) -> bytes:
        lines = stego_text.splitlines()

        # 1. קריאת ה-Header (32 הביטים הראשונים)
        if len(lines) < self.HEADER_BITS:
            raise CorruptedPayloadError()

        header_bits = []
        for i in range(self.HEADER_BITS):
            # חישוב כמות הרווחים בסוף השורה
            trailing_spaces = len(lines[i]) - len(lines[i].rstrip(' '))
            
            if trailing_spaces == 1:
                header_bits.append(0)
            elif trailing_spaces == 2:
                header_bits.append(1)
            else:
                # אם אין רווחים או שיש יותר מדי, הקובץ פגום או לא מכיל הודעה
                raise CorruptedPayloadError()

        # 2. תרגום ה-Header למספר (אורך ההודעה בבייטים)
        length_bytes = bytearray()
        for i in range(0, self.HEADER_BITS, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | header_bits[i + j]
            length_bytes.append(byte)
        
        payload_length = int.from_bytes(length_bytes, "big")

        # 3. בדיקת תקינות: האם יש מספיק שורות להמשך ההודעה?
        total_payload_bits = payload_length * 8
        if len(lines) < self.HEADER_BITS + total_payload_bits:
            raise CorruptedPayloadError()

        # 4. חילוץ ביטי ההודעה (החל משורה 32)
        payload_bits = []
        for i in range(self.HEADER_BITS, self.HEADER_BITS + total_payload_bits):
            trailing_spaces = len(lines[i]) - len(lines[i].rstrip(' '))
            
            if trailing_spaces == 1:
                payload_bits.append(0)
            elif trailing_spaces == 2:
                payload_bits.append(1)
            else:
                raise CorruptedPayloadError()

        # 5. המרת הביטים חזרה לבייטים
        payload = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload_bits[i + j]
            payload.append(byte)

        return bytes(payload)