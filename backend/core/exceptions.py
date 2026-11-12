class KnovaException(Exception):
    """
    Base exception for all KNOVA application errors.
    Every custom exception in the app should inherit from this,
    so we can catch "any KNOVA error" in one place if needed.
    """

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(KnovaException):
    """Raised when a requested resource (document, workspace, user, etc.) doesn't exist."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class PermissionDeniedError(KnovaException):
    """Raised when a user tries to access something they don't have rights to."""

    def __init__(self, message: str = "You do not have permission to do this"):
        super().__init__(message, status_code=403)


class ValidationError(KnovaException):
    """Raised when input data is invalid (bad file type, missing field, etc.)."""

    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, status_code=400)


class ServiceUnavailableError(KnovaException):
    """Raised when a dependency (database, vector store, LLM provider) is unreachable."""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, status_code=503)