class DomainError(Exception):
    """Base class for all business/domain errors."""

    pass


# ---------------------------
# Stego / Crypto errors
# ---------------------------
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


# ---------------------------
# User/Auth errors
# ---------------------------
class UserNotFoundError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class UserAlreadyExistsError(DomainError):
    pass


# ---------------------------
# File/Share errors
# ---------------------------
class FileNotFoundError(DomainError):
    pass


class FileAccessDeniedError(DomainError):
    pass


class FileVersionNotFoundError(DomainError):
    pass


class FileOwnershipError(DomainError):
    pass


class FileAlreadySharedError(DomainError):
    pass


class SelfShareNotAllowedError(DomainError):
    pass


class ConversationNotFoundError(DomainError):
    pass


class ConversationAccessDeniedError(DomainError):
    pass


class InvalidConversationParticipantError(DomainError):
    pass


class MessageNotFoundError(DomainError):
    pass
