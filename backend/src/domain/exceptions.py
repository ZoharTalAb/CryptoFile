class DomainError(Exception):
    pass


class UnsupportedAudioFormatError(DomainError):
    pass


class PayloadTooLargeError(DomainError):
    pass


class CorruptedPayloadError(DomainError):
    pass


class InvalidPasswordError(DomainError):
    pass


class InvalidSaltError(DomainError):
    pass


class InvalidWrappedKeyError(DomainError):
    pass


class InvalidKeyLengthError(DomainError):
    pass


class DecryptionFailedError(DomainError):
    pass
