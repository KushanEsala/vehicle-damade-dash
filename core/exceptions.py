from __future__ import annotations


class ERPBaseException(Exception):
    """Base exception for Vehicle Damage ERP."""
    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__


class ConfigurationError(ERPBaseException):
    """Raised when environment or app configuration is invalid."""


class AuthenticationError(ERPBaseException):
    """Raised when login or credentials verification fails."""


class AuthorizationError(ERPBaseException):
    """Raised when user lacks permission for an action."""


class AccountLockedError(AuthenticationError):
    """Raised when account is locked due to failed login attempts."""


class PasswordChangeRequiredError(AuthenticationError):
    """Raised when user must change password before proceeding."""


class ResourceNotFoundError(ERPBaseException):
    """Raised when a requested DB record or file is not found."""


class DuplicateResourceError(ERPBaseException):
    """Raised when a unique constraint is violated."""


class ValidationError(ERPBaseException):
    """Raised when input validation fails."""


class ModelInferenceError(ERPBaseException):
    """Raised when model inference or file loading fails."""


class StorageError(ERPBaseException):
    """Raised when file storage read/write fails."""
