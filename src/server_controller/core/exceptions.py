
class ProcessCreationFailed(Exception):
    def __init__(self, message="Process Creation Failed"):
        self.message = message
        super().__init__(self.message)

class ProcessDoesNotExist(Exception):
    def __init__(self, message="Process Does Not Exist"):
        self.message = message
        super().__init__(self.message)

class ProcessAlreadyExistsError(Exception):
    def __init__(self, message="Process Already Exists"):
        self.message = message
        super().__init__(self.message)

class ProcessValidationFailed(Exception):
    def __init__(self, message='Process Validation Failed'):
        self.message = message
        super().__init__(self.message)
