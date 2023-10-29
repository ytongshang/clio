import logging

import colorlog


def _console_handler(_logger):
    _formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)5s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARN": "yellow",
            "ERROR": "red",
            "FATAL": "bold_red",
        },
    )
    _handler = logging.StreamHandler()
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)
    _logger.setLevel(logging.DEBUG)


default_logger = colorlog.getLogger()
_console_handler(default_logger)


class Log:
    @staticmethod
    def debug(msg, *args, **kwargs):
        default_logger.debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        default_logger.info(msg, *args, **kwargs)

    @staticmethod
    def warn(msg, *args, **kwargs):
        default_logger.warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        exec_info = kwargs.pop("exc_info", True)
        default_logger.error(msg, *args, exc_info=exec_info, **kwargs)

    @staticmethod
    def fatal(msg, *args, **kwargs):
        default_logger.critical(msg, *args, exc_info=True, **kwargs)

    @staticmethod
    def exception(msg="", *args, **kwargs):
        default_logger.exception(msg, *args, exc_info=True, **kwargs)
