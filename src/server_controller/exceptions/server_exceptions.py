class ProcessAlreadyExistsError(Exception):
    def __init__(self, message="Server Is Already Running"):
        self.message = message
        super().__init__(self.message)


class ProcessDoesNotExist(Exception):
    def __init__(self, message="Server Is Not Running"):
        self.message = message
        super().__init__(self.message)


class ProcessCreationFailed(Exception):
    def __init__(self, message="Server Creation Failed"):
        self.message = message
        super().__init__(self.message)


class ProcessValidationFailed(Exception):
    def __init__(self, message="Server Failed During Run"):
        self.message = message
        super().__init__(self.message)


class ServerConnectionFailed(Exception):
    def __init__(self, message="Server Failed During Run"):
        self.message = message
        super().__init__(self.message)