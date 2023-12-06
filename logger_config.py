# logger_config.py
import logging


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create FileHandler
    handler = logging.FileHandler("./logs.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # add FileHandler to logger
    logger.addHandler(handler)

    return logger
