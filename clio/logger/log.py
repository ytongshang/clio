import glob
import logging
import os
from datetime import datetime

import colorlog

from clio.context import TraceContext
from clio.context.trace import trace_context

logging.basicConfig(level=logging.DEBUG)
default_logger = logging.getLogger("clio")


class CustomFileHandler(logging.FileHandler):
    def emit(self, record):
        extra_map = trace_context.trace_extra()
        trace_id = extra_map.pop(TraceContext.X_TRACE_ID, None)
        lines = []
        if trace_id:
            lines.append(f"{trace_id} ｜")
        if extra_map:
            lines.append("[")
            for k, v in extra_map.items():
                lines.append(f"{str(k)}={str(v)}")
            lines.append("]")
        lines.append(record.msg)
        record.msg = " ".join(lines)
        super().emit(record)


def console_handler(log_level=logging.DEBUG):
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
    _handler.setLevel(log_level)
    return _handler


def file_handler(
    log_dir,
    file_max_keep_days=7,
    logging_level=logging.INFO,
    log_format="%(asctime)s | %(levelname)s | %(message)s",
):
    current_date = datetime.now()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    for log_file in glob.glob(os.path.join(log_dir, "*.log")):
        file_date_str = os.path.basename(log_file).split(".")[0]
        file_date = datetime.strptime(file_date_str, "%Y_%m_%d")
        days_difference = (current_date - file_date).days
        if days_difference > file_max_keep_days:
            try:
                os.remove(log_file)
            except Exception as e:
                pass

    time = datetime.now().strftime("%Y_%m_%d")
    log_file_handler = CustomFileHandler(f"{log_dir}/{time}.log")
    log_file_handler.setLevel(logging_level)
    log_file_handler.setFormatter(logging.Formatter(log_format))
    return log_file_handler


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
