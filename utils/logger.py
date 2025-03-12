import logging
import sys


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Choose a color based on the log level
        if record.levelno == logging.DEBUG:
            color = BColors.OKBLUE
        elif record.levelno == logging.INFO:
            color = BColors.OKGREEN
        elif record.levelno == logging.WARNING:
            color = BColors.WARNING
        elif record.levelno == logging.ERROR:
            color = BColors.FAIL
        elif record.levelno == logging.CRITICAL:
            color = BColors.HEADER
        else:
            color = BColors.ENDC

        # Format the message with color
        record.msg = f"{color}{record.msg}{BColors.ENDC}"
        return super().format(record)


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if they already exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


default_logger = setup_logger(__name__)
