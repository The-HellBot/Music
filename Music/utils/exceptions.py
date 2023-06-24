class UserException(Exception):
    def __init__(self, error: str):
        super().__init__(error)


class CarbonException(Exception):
    def __init__(self, error: str):
        super().__init__(error)