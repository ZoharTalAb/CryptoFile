import io
import wave
from domain.exceptions import CorruptedPayloadError
from domain.exceptions import PayloadTooLargeError
from domain.exceptions import UnsupportedAudioFormatError


class AudioStegoEngine:
    def embed(self, audio_bytes: bytes, encrypted_payload: bytes) -> bytes:
        buffer = io.BytesIO(audio_bytes)

        with wave.open(buffer, "rb") as wav:
            if wav.getsampwidth() != 2:
                raise UnsupportedAudioFormatError()

            frames = wav.readframes(wav.getnframes())
            params = wav.getparams()

        samples = bytearray(frames)

        # Prepare payload with 4-byte length header
        length_header = len(encrypted_payload).to_bytes(4, "big")
        full_payload = length_header + encrypted_payload

        total_samples = len(samples) // 2
        max_payload_bytes = (total_samples // 8) - 4

        if len(encrypted_payload) > max_payload_bytes:
            raise PayloadTooLargeError()

        bit_index = 0
        payload_bits = []

        for byte in full_payload:
            for i in range(8):
                payload_bits.append((byte >> (7 - i)) & 1)

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

            frames = wav.readframes(wav.getnframes())

        samples = bytearray(frames)

        # Read first 32 bits → payload length
        bits = []
        for i in range(32):
            sample_byte_index = i * 2
            bit = samples[sample_byte_index] & 1
            bits.append(bit)

        # Convert bits to length
        length_bytes = bytearray()
        for i in range(0, 32, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            length_bytes.append(byte)

        payload_length = int.from_bytes(length_bytes, "big")
        if payload_length < 0:
            raise CorruptedPayloadError()

        # Now read payload bits
        total_payload_bits = payload_length * 8
        total_samples = len(samples) // 2

        if 32 + total_payload_bits > total_samples:
            raise CorruptedPayloadError()

        payload_bits = []

        for i in range(32, 32 + total_payload_bits):
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
