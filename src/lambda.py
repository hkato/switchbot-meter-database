import os
import urllib.parse

import requests

from switchbot_meter_database.main import main


def get_secret_from_extension(parameter_name, with_decryption=False):
    """Get secret value from AWS Parameters and Secrets Extension"""
    encoded_parameter_name = urllib.parse.quote(parameter_name, safe="/")
    url = f"http://localhost:2773/systemsmanager/parameters/get/?name={encoded_parameter_name}"
    if with_decryption:
        url += "&withDecryption=true"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["Parameter"]["Value"]


def set_environment_variables_from_parameter_store():
    """Set environment variables from AWS Parameters and Secrets Extension"""
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


def handler(event, context):
    """AWS Lambda handler function"""
    print("Handler invoked with event: %s", event)

    # Set environment variables
    set_environment_variables_from_parameter_store()

    # Run main function
    main()

    return {"statusCode": 200, "body": "OK"}
