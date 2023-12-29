class StarletteContextError(Exception):
    pass


class ContextDoesNotExistError(RuntimeError, StarletteContextError):
    def __init__(self):
        self.message = (
            "You didn't use the required middleware or "
            "you're trying to access `context` object "
            "outside of the request-response cycle."
        )
        super().__init__(self.message)
