import logging

logging.basicConfig(datefmt='%d-%b-%Y %I:%M:%S', level=logging.INFO)

def get_logger(name: str):
    return logging.getLogger(name)