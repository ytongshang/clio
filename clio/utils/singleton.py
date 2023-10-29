import abc
from typing import Any


class Singleton(abc.ABCMeta, type):
    _instances: dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


#
class AbstractSingleton(abc.ABC, metaclass=Singleton):
    """单例基类."""
