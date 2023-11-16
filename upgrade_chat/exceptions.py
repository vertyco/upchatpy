class APIError(Exception):
    """General exception for API-related errors."""

    def __init__(self, status_code, message=None):
        self.status_code = status_code
        super().__init__(message or f"HTTP error occurred: {status_code}")


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class HTTPError(APIError):
    """Exception for HTTP errors during API requests."""


class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found."""
