import logging
import os
import sys
import urllib.parse

import requests

from switchbot_meter_database.main import main


def get_secret_from_extension(parameter_name, with_decryption=False):
    encoded_parameter_name = urllib.parse.quote(parameter_name, safe="/")

    url = f"http://localhost:2773/systemsmanager/parameters/get/?name={encoded_parameter_name}"
    if with_decryption:
        url += "&withDecryption=true"

    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["Parameter"]["Value"]


def handler(event, context):
    """
    AWS Lambda handler function
    """
    # Set environment variables from AWS Parameters and Secrets Extension
    os.environ["SWITCHBOT_TOKEN"] = get_secret_from_extension(
        os.environ.get("SWITCHBOT_TOKEN_PATH", "/switchbot-meter-database/switchbot-token"), True
    )
    os.environ["SWITCHBOT_SECRET"] = get_secret_from_extension(
        os.environ.get("SWITCHBOT_SECRET_PATH", "/switchbot-meter-database/switchbot-secret"), True
    )
    os.environ["DATABASE"] = get_secret_from_extension(
        os.environ.get("DATABASE_PATH", "/switchbot-meter-database/database")
    )
    os.environ["MONGODB_URI"] = get_secret_from_extension(
        os.environ.get("MONGODB_URI_PATH", "/switchbot-meter-database/mongodb-uri"), True
    )
    os.environ["MONGODB_DATABASE"] = get_secret_from_extension(
        os.environ.get("MONGODB_DATABASE_PATH", "/switchbot-meter-database/mongodb-database")
    )
    os.environ["MONGODB_COLLECTION"] = get_secret_from_extension(
        os.environ.get("MONGODB_COLLECTION_PATH", "/switchbot-meter-database/mongodb-collection")
    )

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
