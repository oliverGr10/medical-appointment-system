class DomainException(Exception):
    """Base exception for domain errors"""
    pass


class UnauthorizedError(DomainException):
    """Raised when a user tries to perform an unauthorized action"""
    pass
