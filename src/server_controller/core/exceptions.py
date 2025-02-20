class ProcessDoesNotExist(Exception):
    def __init__(self, message="Process Does Not Exist"):
        self.message = message
        super().__init__(self.message)

class ProcessAlreadyExistsError(Exception):
    def __init__(self, message="Process Already Exists"):
        self.message = message
        super().__init__(self.message)

class ProcessNotRunning(Exception):
    def __init__(self, message='Process Not Running'):
        self.message = message
        super().__init__(self.message)

class CommandNotAllowed(Exception):
    def __init__(self, message=None):
        self.message = f'Command: `{message}` not allowed'
        super().__init__(self.message)
