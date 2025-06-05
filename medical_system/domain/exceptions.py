
class DomainException(Exception):
    def __init__(self, message: str = "A domain error occurred", code: str = None):
        self.message = message
        self.code = code or "domain_error"
        super().__init__(self.message)

class UnauthorizedError(DomainException):
    def __init__(self, message: str = "Unauthorized access", code: str = None):
        super().__init__(message or "You don't have permission to perform this action", code or "unauthorized")

class ValidationError(DomainException):
    def __init__(self, message: str = "Invalid input data", code: str = None, errors: dict = None):
        self.errors = errors or {}
        super().__init__(message, code or "validation_error")

class ResourceNotFoundError(DomainException):
    def __init__(self, message: str = "The requested resource was not found", code: str = None):
        super().__init__(message, code or "not_found")

class BusinessRuleViolationError(DomainException):
    def __init__(self, message: str = "Business rule violation", code: str = None):
        super().__init__(message, code or "business_rule_violation")

class ConflictError(DomainException):
    def __init__(self, message: str = "Resource conflict", code: str = None):
        super().__init__(message, code or "conflict")

class ServiceUnavailableError(DomainException):
    def __init__(self, message: str = "Service unavailable", code: str = None):
        super().__init__(message, code or "service_unavailable")

class RateLimitExceededError(DomainException):
    def __init__(self, message: str = "Rate limit exceeded", code: str = None, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, code or "rate_limit_exceeded")
