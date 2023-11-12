import functools
import inspect
import time

from clio.utils import Log, Performance, short_json
from clio.web import HttpResponse

from .common import is_async_function

"""
    用于打印函数的输入输出日志,包括函数名,参数,返回值,执行时间，还可用于性能分析 覆盖了@timing_decorator的功能
"""


def _format_result(result):
    if isinstance(result, HttpResponse):
        return short_json(result)
    else:
        return str(result)


def logger(func):
    module_name = inspect.getmodule(func).__name__
    function_name = func.__name__
    is_async = is_async_function(func)

    if is_async:

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            Performance().add(module_name, function_name, elapsed_time)
            Log.info(
                "async invoke 【{}.{}】 elapsed_time:【{}】 ,param:【{},{}】 ,result:【{}】".format(
                    module_name,
                    function_name,
                    elapsed_time,
                    str(args),
                    str(kwargs),
                    _format_result(result),
                )
            )
            return result

        return wrapper

    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            Performance().add(module_name, function_name, elapsed_time)
            Log.info(
                "sync invoke 【{}.{}】 elapsed_time:【{}】 ,param:【{},{}】 ,result:【{}】".format(
                    module_name,
                    function_name,
                    elapsed_time,
                    str(args),
                    str(kwargs),
                    _format_result(result),
                )
            )
            return result

        return wrapper
