from domain.interfaces.stego_engine import StegoEngine
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError


class VideoStegoEngine(StegoEngine):
    """
    Container-safe video steganography engine.

    Instead of re-encoding frames (which breaks browser playback and is fragile
    under lossy codecs), this engine appends a hidden trailer to the end of the
    video file:

        [original video bytes][payload][payload_length:8 bytes][magic]

    Most players and browsers ignore trailing bytes after the valid video
    container, so playback remains intact while extraction stays deterministic.
    """

    MAGIC = b"CRYPTOFILE_VIDEO_STEGO_V1"
    LENGTH_SIZE = 8
    MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB safety cap

    def embed(self, video_bytes: bytes, payload: bytes) -> bytes:
        if not video_bytes:
            raise CorruptedPayloadError("Video file is empty")

        if payload is None:
            raise CorruptedPayloadError("Payload is missing")

        if len(payload) > self.MAX_PAYLOAD_BYTES:
            raise PayloadTooLargeError("Payload is too large for video stego")

        if video_bytes.endswith(self.MAGIC):
            raise CorruptedPayloadError(
                "Video already appears to contain a stego trailer"
            )

        payload_length = len(payload).to_bytes(self.LENGTH_SIZE, "big")

        return video_bytes + payload + payload_length + self.MAGIC

    def extract(self, video_bytes: bytes) -> bytes:
        if not video_bytes:
            raise CorruptedPayloadError("Video file is empty")

        minimum_size = len(self.MAGIC) + self.LENGTH_SIZE
        if len(video_bytes) < minimum_size:
            raise CorruptedPayloadError("Video does not contain a valid stego trailer")

        if not video_bytes.endswith(self.MAGIC):
            raise CorruptedPayloadError(
                "Could not find a valid hidden payload in video"
            )

        magic_start = len(video_bytes) - len(self.MAGIC)
        length_end = magic_start
        length_start = length_end - self.LENGTH_SIZE

        if length_start < 0:
            raise CorruptedPayloadError("Corrupted stego trailer")

        payload_length = int.from_bytes(video_bytes[length_start:length_end], "big")

        if payload_length < 0 or payload_length > self.MAX_PAYLOAD_BYTES:
            raise CorruptedPayloadError("Invalid hidden payload length")

        payload_start = length_start - payload_length
        if payload_start < 0:
            raise CorruptedPayloadError("Corrupted hidden payload boundaries")

        return video_bytes[payload_start:length_start]
