import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        filemode="w",
        filename="py_log.log",
        format="%(asctime)s %(levelname)s %(message)s" 
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)