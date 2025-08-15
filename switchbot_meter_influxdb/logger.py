import logging


def set_logger():
    logger = logging.getLogger()

    streamHandler = logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(levelname)-8s] %(asctime)s %(funcName)s %(message)s"
    )

    streamHandler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    streamHandler.setLevel(logging.INFO)

    logger.addHandler(streamHandler)

    return logger
