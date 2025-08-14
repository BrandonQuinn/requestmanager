import logging
import os

def get_logger(name: str, log_file: str = 'app.log', level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger  # Already configured, don’t be dumb and double it

    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger