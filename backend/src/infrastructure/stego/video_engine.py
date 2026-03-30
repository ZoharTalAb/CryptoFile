from __future__ import annotations

from domain.interfaces.stego_engine import StegoEngine
from domain.exceptions import CorruptedPayloadError, PayloadTooLargeError


class VideoStegoEngine(StegoEngine):
    BOX_TYPE = b"uuid"
    BOX_UUID = bytes.fromhex("7d6f6e51c9d54d9d9b7f5a9d3c4e1f20")
    MAGIC = b"CRYPTOFILE_VIDEO_STEGO_V2"
    LENGTH_SIZE = 8
    MAX_PAYLOAD_BYTES = 10 * 1024 * 1024

    def embed(self, video_bytes: bytes, payload: bytes) -> bytes:
        if not video_bytes:
            raise CorruptedPayloadError("Video file is empty")

        if payload is None:
            raise CorruptedPayloadError("Payload is missing")

        if len(payload) > self.MAX_PAYLOAD_BYTES:
            raise PayloadTooLargeError("Payload too large")

        if not self._looks_like_mp4(video_bytes):
            raise CorruptedPayloadError("Only MP4 supported")

        if self._has_stego_box(video_bytes):
            raise CorruptedPayloadError("Video already contains stego")

        body = (
            self.BOX_UUID
            + self.MAGIC
            + len(payload).to_bytes(self.LENGTH_SIZE, "big")
            + payload
        )

        size = 8 + len(body)
        box = size.to_bytes(4, "big") + self.BOX_TYPE + body

        return video_bytes + box

    def extract(self, video_bytes: bytes) -> bytes:
        if not video_bytes:
            raise CorruptedPayloadError("Video file is empty")

        if not self._looks_like_mp4(video_bytes):
            raise CorruptedPayloadError("Only MP4 supported")

        result = self._extract_from_tail(video_bytes)
        if result is None:
            raise CorruptedPayloadError("Could not find hidden payload")

        return result

    def _looks_like_mp4(self, data: bytes) -> bool:
        return b"ftyp" in data[:64]

    def _has_stego_box(self, data: bytes) -> bool:
        return self._extract_from_tail(data) is not None

    def _extract_from_tail(self, data: bytes) -> bytes | None:
        magic_index = data.rfind(self.MAGIC)
        if magic_index == -1:
            return None

        uuid_start = magic_index - len(self.BOX_UUID)
        if uuid_start < 8:
            raise CorruptedPayloadError("Corrupted video stego structure")

        # Validate uuid
        uuid_value = data[uuid_start:magic_index]
        if uuid_value != self.BOX_UUID:
            raise CorruptedPayloadError("Invalid video stego UUID")

        # Validate box header
        type_start = uuid_start - 4
        size_start = uuid_start - 8

        if size_start < 0:
            raise CorruptedPayloadError("Invalid video stego header")

        box_type = data[type_start:uuid_start]
        if box_type != self.BOX_TYPE:
            raise CorruptedPayloadError("Invalid video stego box type")

        box_size = int.from_bytes(data[size_start:type_start], "big")
        actual_box_size = len(data) - size_start

        if box_size != actual_box_size:
            raise CorruptedPayloadError("Corrupted video stego box length")

        length_start = magic_index + len(self.MAGIC)
        length_end = length_start + self.LENGTH_SIZE

        if length_end > len(data):
            raise CorruptedPayloadError("Corrupted hidden payload length")

        payload_length = int.from_bytes(data[length_start:length_end], "big")

        if payload_length < 0 or payload_length > self.MAX_PAYLOAD_BYTES:
            raise CorruptedPayloadError("Invalid hidden payload length")

        payload_start = length_end
        payload_end = payload_start + payload_length

        if payload_end != len(data):
            raise CorruptedPayloadError("Corrupted hidden payload boundaries")

        return data[payload_start:payload_end]
