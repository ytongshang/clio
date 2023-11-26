import glob
import logging
import os
from datetime import datetime

import colorlog


def console_handler(logger):
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
    logger.addHandler(_handler)
    logger.setLevel(logging.DEBUG)


def file_handler(
    logger,
    log_dir,
    file_max_keep_days=7,
    logging_level=logging.DEBUG,
    log_format="%(asctime)s | %(levelname)s | %(message)s",
):
    current_date = datetime.now()
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
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_handler = logging.FileHandler(f"{log_dir}/{time}.log")
    log_file_handler.setLevel(logging_level)
    formatter = logging.Formatter(log_format)
    log_file_handler.setFormatter(formatter)
    logger.addHandler(log_file_handler)


default_logger = logging.getLogger()


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
