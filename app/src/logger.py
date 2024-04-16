""" custom logger for stream handler and formating """

import logging


def get_logger():
    """Returns the pystats_logger logging obj. Creates new logging obj if it does not exist."""
    log = logging.getLogger("pystats_logger")
    if not log.handlers:
        log.setLevel(logging.DEBUG)
        lsh = logging.StreamHandler()
        log_formater = logging.Formatter(
            "%(created)17s;%(levelname)8s;%(message)s",
        )
        lsh.setFormatter(log_formater)
        log.addHandler(lsh)
        log.propagate = False
    return log
