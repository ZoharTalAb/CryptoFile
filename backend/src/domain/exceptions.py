class DomainError(Exception):
    pass


class UnsupportedAudioFormatError(DomainError):
    pass


class PayloadTooLargeError(DomainError):
    pass


class CorruptedPayloadError(DomainError):
    pass
