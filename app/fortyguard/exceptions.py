class FortyGuardError(RuntimeError):
    pass

class FortyGuardConfigurationError(FortyGuardError):
    pass

class FortyGuardAccessError(FortyGuardError):
    pass

class FortyGuardRequestError(FortyGuardError):
    def __init__(self, message: str, status_code: int | None = None, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

class FortyGuardTimeoutError(FortyGuardError):
    pass
