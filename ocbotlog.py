import logging
import sys

LOGGER_NAME = "ocbotlog"

def prep():
    logger = logging.getLogger(LOGGER_NAME)
    sh = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter('[%(levelname)s] [%(asctime)s]: %(message)s')
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)

def getLogger():
    return logging.getLogger(LOGGER_NAME)
