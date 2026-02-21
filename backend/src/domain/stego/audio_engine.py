import io
import wave

from domain.exceptions import (
    CorruptedPayloadError,
    PayloadTooLargeError,
    UnsupportedAudioFormatError,
)


class AudioStegoEngine:
    HEADER_BITS = 32  # 4 bytes length header

    def embed(self, audio_bytes: bytes, encrypted_payload: bytes) -> bytes:
        buffer = io.BytesIO(audio_bytes)

        with wave.open(buffer, "rb") as wav:
            if wav.getsampwidth() != 2:
                raise UnsupportedAudioFormatError()

            if wav.getcomptype() != "NONE":
                raise UnsupportedAudioFormatError()

            if wav.getnchannels() < 1:
                raise UnsupportedAudioFormatError()

            frames = wav.readframes(wav.getnframes())
            params = wav.getparams()

        samples = bytearray(frames)
        total_samples = len(samples) // 2

        # Must have enough samples to even store header
        if total_samples < self.HEADER_BITS:
            raise PayloadTooLargeError()

        # Prepare payload with 4-byte length header
        length_header = len(encrypted_payload).to_bytes(4, "big")
        full_payload = length_header + encrypted_payload

        max_payload_bytes = (total_samples // 8) - 4

        if len(encrypted_payload) > max_payload_bytes:
            raise PayloadTooLargeError()

        # Convert payload to bits
        payload_bits = []
        for byte in full_payload:
            for i in range(8):
                payload_bits.append((byte >> (7 - i)) & 1)

        # Embed bits into LSB of each sample
        for i, bit in enumerate(payload_bits):
            sample_byte_index = i * 2
            samples[sample_byte_index] = (samples[sample_byte_index] & 0xFE) | bit

        # Rebuild WAV
        output_buffer = io.BytesIO()
        with wave.open(output_buffer, "wb") as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(bytes(samples))

        return output_buffer.getvalue()

    def extract(self, audio_bytes: bytes) -> bytes:
        buffer = io.BytesIO(audio_bytes)

        with wave.open(buffer, "rb") as wav:
            if wav.getsampwidth() != 2:
                raise UnsupportedAudioFormatError()

            if wav.getcomptype() != "NONE":
                raise UnsupportedAudioFormatError()

            if wav.getnchannels() < 1:
                raise UnsupportedAudioFormatError()

            frames = wav.readframes(wav.getnframes())

        samples = bytearray(frames)
        total_samples = len(samples) // 2

        if total_samples < self.HEADER_BITS:
            raise CorruptedPayloadError()

        # Read first 32 bits → payload length
        bits = []
        for i in range(self.HEADER_BITS):
            sample_byte_index = i * 2
            bit = samples[sample_byte_index] & 1
            bits.append(bit)

        length_bytes = bytearray()
        for i in range(0, self.HEADER_BITS, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            length_bytes.append(byte)

        payload_length = int.from_bytes(length_bytes, "big")

        # Hard safety validation
        max_possible_payload = total_samples // 8
        if payload_length > max_possible_payload:
            raise CorruptedPayloadError()

        total_payload_bits = payload_length * 8

        if self.HEADER_BITS + total_payload_bits > total_samples:
            raise CorruptedPayloadError()

        # Read payload bits
        payload_bits = []
        for i in range(self.HEADER_BITS, self.HEADER_BITS + total_payload_bits):
            sample_byte_index = i * 2
            bit = samples[sample_byte_index] & 1
            payload_bits.append(bit)

        # Convert bits back to bytes
        payload = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload_bits[i + j]
            payload.append(byte)

        return bytes(payload)
