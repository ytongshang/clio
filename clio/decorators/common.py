import inspect


def is_async_function(func):
    return inspect.isasyncgenfunction(func) or inspect.iscoroutinefunction(func)
