import os

from dotenv import load_dotenv

from clio.utils.log import console_handler, default_logger


def load_env():
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    # Load the .env file into environment variables
    _env_file_path = os.path.join(_current_dir, "../.env")
    load_dotenv(dotenv_path=_env_file_path, verbose=True)


console_handler(default_logger)
load_env()
