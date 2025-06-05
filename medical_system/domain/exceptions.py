
class DomainException(Exception):
    def __init__(self, message: str = "Ocurrió un error en el dominio", code: str = None):
        self.message = message
        self.code = code or "error_dominio"
        super().__init__(self.message)

class BadRequestError(DomainException):
    def __init__(self, message: str = "Solicitud incorrecta", code: str = None):
        super().__init__(message, code or "solicitud_incorrecta")

class UnauthorizedError(DomainException):
    def __init__(self, message: str = "Acceso no autorizado", code: str = None):
        super().__init__(message or "No tienes permiso para realizar esta acción", code or "no_autorizado")

class ValidationError(DomainException):
    def __init__(self, message: str = "Datos de entrada no válidos", code: str = None, errors: dict = None):
        self.errors = errors or {}
        super().__init__(message, code or "validacion_fallida")

class ResourceNotFoundError(DomainException):
    def __init__(self, message: str = "El recurso solicitado no fue encontrado", code: str = None):
        super().__init__(message, code or "recurso_no_encontrado")

NotFoundError = ResourceNotFoundError

class BusinessRuleViolationError(DomainException):
    def __init__(self, message: str = "Violación de regla de negocio", code: str = None):
        super().__init__(message, code or "violacion_regla_negocio")
