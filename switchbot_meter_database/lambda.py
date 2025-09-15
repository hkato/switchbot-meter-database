import logging
import sys

from .main import main


def handler(event, context):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-8s] %(funcName)s %(message)s",
        stream=sys.stdout,
    )

    logger = logging.getLogger(__name__)
    logger.info("Handler invoked with event: %s", event)

    main()

    return {"statusCode": 200, "body": "OK"}
