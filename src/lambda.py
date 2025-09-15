import logging
import os
import sys

import boto3

from switchbot_meter_database.main import main


def set_env_from_ssm():
    ssm_client = boto3.client("ssm")

    response = ssm_client.get_parameter(
        Name=os.environ.get(
            "SWITCHBOT_TOKEN_PATH", "/switchbot-meter-database/switchbot-token"
        ),
        WithDecryption=True,
    )
    os.environ["SWITCHBOT_TOKEN"] = response["Parameter"]["Value"]

    response = ssm_client.get_parameter(
        Name=os.environ.get(
            "SWITCHBOT_SECRET_PATH", "/switchbot-meter-database/switchbot-secret"
        ),
        WithDecryption=True,
    )
    os.environ["SWITCHBOT_SECRET"] = response["Parameter"]["Value"]

    response = ssm_client.get_parameter(
        Name=os.environ.get("DATABASE_PATH", "/switchbot-meter-database/database"),
        WithDecryption=False,
    )
    os.environ["DATABASE"] = response["Parameter"]["Value"]

    response = ssm_client.get_parameter(
        Name=os.environ.get(
            "MONGODB_URI_PATH", "/switchbot-meter-database/mongodb-uri"
        ),
        WithDecryption=True,
    )
    os.environ["MONGODB_URI"] = response["Parameter"]["Value"]

    response = ssm_client.get_parameter(
        Name=os.environ.get(
            "MONGODB_DATABASE_PATH", "/switchbot-meter-database/mongodb-database"
        ),
        WithDecryption=False,
    )
    os.environ["MONGODB_DATABASE"] = response["Parameter"]["Value"]

    response = ssm_client.get_parameter(
        Name=os.environ.get(
            "MONGODB_COLLECTION_PATH", "/switchbot-meter-database/mongodb-collection"
        ),
        WithDecryption=False,
    )
    os.environ["MONGODB_COLLECTION"] = response["Parameter"]["Value"]


def handler(event, context):
    set_env_from_ssm()

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
