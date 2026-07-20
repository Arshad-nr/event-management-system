class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class DuplicateEmailException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            code="DUPLICATE_EMAIL",
            message="Email is already registered"
        )

class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            code="INVALID_CREDENTIALS",
            message="Invalid email or password"
        )

class EventNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            code="EVENT_NOT_FOUND",
            message="Event not found"
        )

class EventFullException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            code="EVENT_FULL",
            message="Event has reached its maximum capacity"
        )

class AlreadyRegisteredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            code="ALREADY_REGISTERED",
            message="Student is already registered for this event"
        )
