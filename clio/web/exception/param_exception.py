# 参数不正常异常
class ParamException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return "ParamException: " + self.message


# 检查参数是不为空，且类型为data_type
def check_not_null(name, value, data_type):
    if value is None:
        raise ParamException(f"value {name} can not be null")
    if not isinstance(value, data_type):
        raise ParamException(f"value {name} must be {data_type}")


def validate(data, data_type):
    if data is None:
        raise ParamException(f"{data_type} can not be null")
    try:
        data_value = data_type(**data)
        return data_value
    except Exception as e:
        raise ParamException(str(e))
