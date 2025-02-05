class ProcessAlreadyExistsError(Exception):
    def __init__(self, message="Process Already Exists"):
        self.message = message
        super().__init__(self.message)


class ProcessDoesNotExist(Exception):
    def __init__(self, message="Process Does Not Exist"):
        self.message = message
        super().__init__(self.message)


class ProcessCreationFailed(Exception):
    def __init__(self, message="Process Start Failed"):
        self.message = message
        super().__init__(self.message)


class ProcessFailedDuringRun(Exception):
    def __init__(self, message="Process Failed During Run"):
        self.message = message
        super().__init__(self.message)