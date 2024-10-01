# 参数不正常异常
class ParamException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return "ParamException: " + self.message
