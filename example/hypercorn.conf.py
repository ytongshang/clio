import logging
import os

# https://hypercorn.readthedocs.io/en/latest/how_to_guides/configuring.html#configuration-options


# bind
bind = "0.0.0.0:8000"

# workers
num_cpu = os.cpu_count() or 1
workers = 2 * int(num_cpu) + 1

# keepalive
keep_alive_timeout = 2

# headers
include_server_header = False

# hypercorn.logging.Logger
# access_log
loglevel = "info"
_logger = logging.getLogger()
accesslog = _logger
# error_log
errorlog = _logger
