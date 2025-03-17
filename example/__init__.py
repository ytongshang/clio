import logging
import os

from dotenv import load_dotenv

from clio.logger import console_handler, default_logger, file_handler
from clio.utils import hack_json
from clio.workspace import Workspace


def load_env():
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    # Load the .env file into environment variables
    _env_file_path = os.path.join(_current_dir, "../.env")
    load_dotenv(dotenv_path=_env_file_path, verbose=True)


def init_logger():
    console_ = console_handler(logging.DEBUG)
    default_logger.addHandler(console_)
    log_dir = str(Workspace.default().get_path("logs").resolve())
    file_ = file_handler(log_dir, logging.DEBUG)
    default_logger.addHandler(file_)


def init_workspace():
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _workspace = os.path.join(_current_dir, "../workspace")
    default_workspace = Workspace.make_workspace(_workspace)
    Workspace.save_workspace(Workspace.default_workspace_name, default_workspace)


hack_json()
init_workspace()
init_logger()
load_env()
