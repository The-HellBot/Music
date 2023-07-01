class HellBotException(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)


class ChangeVCException(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)


class JoinGCException(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)


class JoinVCException(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)


class UserException(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)
