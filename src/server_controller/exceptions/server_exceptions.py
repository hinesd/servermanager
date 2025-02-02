class ProcessAlreadyExistsError(Exception):
    def __init__(self, message="Process already exists"):
        self.message = message
        super().__init__(self.message)


class ProcessDoesNotExist(Exception):
    def __init__(self, message="Process does not exist"):
        self.message = message
        super().__init__(self.message)


class ProcessStartFailed(Exception):
    def __init__(self, message="Process start failed"):
        self.message = message
        super().__init__(self.message)