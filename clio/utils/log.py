import glob
import logging
import os
from datetime import datetime

import colorlog

default_logger = logging.getLogger()


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


class Log:
    @staticmethod
    def debug(msg, *args, **kwargs):
        kwargs = Log._logging_extra(**kwargs)
        default_logger.debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        kwargs = Log._logging_extra(**kwargs)
        default_logger.info(msg, *args, **kwargs)

    @staticmethod
    def warn(msg, *args, **kwargs):
        kwargs = Log._logging_extra(**kwargs)
        default_logger.warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        exec_info = kwargs.pop("exc_info", True)
        kwargs = Log._logging_extra(**kwargs)
        default_logger.error(msg, *args, exc_info=exec_info, **kwargs)

    @staticmethod
    def fatal(msg, *args, **kwargs):
        exec_info = kwargs.pop("exc_info", True)
        kwargs = Log._logging_extra(**kwargs)
        default_logger.critical(msg, *args, exc_info=exec_info, **kwargs)

    @staticmethod
    def exception(msg="", *args, **kwargs):
        exec_info = kwargs.pop("exc_info", True)
        kwargs = Log._logging_extra(**kwargs)
        default_logger.exception(msg, *args, exc_info=exec_info, **kwargs)

    @staticmethod
    def _logging_extra(**kwargs):
        sky_extra = kwargs.pop("sky_extra", None)
        if sky_extra is None:
            return {}
        if not isinstance(sky_extra, dict):
            raise Exception("sky_extra must be dict of str, str")
        # 参看logging源码
        # kwargs中必须为extra,然后防止logging内部代码的解包操作,所以包一层,直接在logging中的就可以拿到完成的sky_extra了
        kwargs.update({"extra": {"sky_extra": sky_extra}})
        return kwargs
