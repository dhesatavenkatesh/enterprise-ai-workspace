class PermissionDeniedError(Exception):
    def __init__(
        self,
        message: str = "Permission Denied",
    ) -> None:
        self.message = message
        super().__init__(message)
