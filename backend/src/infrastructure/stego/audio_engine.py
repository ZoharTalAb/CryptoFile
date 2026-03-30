import io
import wave

from domain.interfaces.stego_engine import StegoEngine
from domain.exceptions import (
    CorruptedPayloadError,
    PayloadTooLargeError,
    UnsupportedAudioFormatError,
)


class AudioStegoEngine(StegoEngine):
    """
    WAV-only audio steganography engine.

    Supported carrier format:
    - RIFF/WAVE
    - PCM (comptype == "NONE")
    - 16-bit samples (sampwidth == 2)

    Implementation:
    - 32-bit big-endian payload length header
    - 1 bit embedded in the LSB of the first byte of each 16-bit sample
    """

    HEADER_BITS = 32  # 4-byte payload length header

    def _read_wav(self, audio_bytes: bytes):
        try:
            buffer = io.BytesIO(audio_bytes)
            with wave.open(buffer, "rb") as wav:
                if wav.getcomptype() != "NONE":
                    raise UnsupportedAudioFormatError(
                        "Audio stego supports only uncompressed PCM WAV files"
                    )

                if wav.getsampwidth() != 2:
                    raise UnsupportedAudioFormatError(
                        "Audio stego supports only 16-bit WAV files"
                    )

                if wav.getnchannels() < 1:
                    raise UnsupportedAudioFormatError(
                        "Audio file must contain at least one channel"
                    )

                frames = wav.readframes(wav.getnframes())
                params = wav.getparams()

            return frames, params
        except wave.Error as exc:
            raise UnsupportedAudioFormatError(
                "Audio stego supports only valid WAV files"
            ) from exc

    def embed(self, audio_bytes: bytes, payload: bytes) -> bytes:
        frames, params = self._read_wav(audio_bytes)

        samples = bytearray(frames)
        total_samples = len(samples) // 2

        if total_samples < self.HEADER_BITS:
            raise PayloadTooLargeError("Carrier audio is too small")

        length_header = len(payload).to_bytes(4, "big")
        full_payload = length_header + payload

        max_payload_bytes = (total_samples // 8) - 4
        if len(payload) > max_payload_bytes:
            raise PayloadTooLargeError("Payload is too large for this audio file")

        payload_bits: list[int] = []
        for byte in full_payload:
            for i in range(8):
                payload_bits.append((byte >> (7 - i)) & 1)

        for i, bit in enumerate(payload_bits):
            sample_byte_index = i * 2
            samples[sample_byte_index] = (samples[sample_byte_index] & 0xFE) | bit

        output_buffer = io.BytesIO()
        with wave.open(output_buffer, "wb") as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(bytes(samples))

        return output_buffer.getvalue()

    def extract(self, audio_bytes: bytes) -> bytes:
        frames, _ = self._read_wav(audio_bytes)

        samples = bytearray(frames)
        total_samples = len(samples) // 2

        if total_samples < self.HEADER_BITS:
            raise CorruptedPayloadError("Audio file is too small to contain payload")

        header_bits: list[int] = []
        for i in range(self.HEADER_BITS):
            sample_byte_index = i * 2
            header_bits.append(samples[sample_byte_index] & 1)

        length_bytes = bytearray()
        for i in range(0, self.HEADER_BITS, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | header_bits[i + j]
            length_bytes.append(byte)

        payload_length = int.from_bytes(length_bytes, "big")

        max_possible_payload = (total_samples // 8) - 4
        if payload_length < 0 or payload_length > max_possible_payload:
            raise CorruptedPayloadError("Extracted payload length is invalid")

        total_payload_bits = payload_length * 8
        if self.HEADER_BITS + total_payload_bits > total_samples:
            raise CorruptedPayloadError("Audio payload is incomplete or corrupted")

        payload_bits: list[int] = []
        for i in range(self.HEADER_BITS, self.HEADER_BITS + total_payload_bits):
            sample_byte_index = i * 2
            payload_bits.append(samples[sample_byte_index] & 1)

        payload = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload_bits[i + j]
            payload.append(byte)

        return bytes(payload)
