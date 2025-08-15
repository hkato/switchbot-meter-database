"""Ingest SwitchBot environmental sensor data into InfluxDB or MongoDB"""

import dataclasses
import logging
import os
from typing import List

from switchbot import SwitchBot
from switchbot.devices import Device

from switchbot_meter_database.devices import SUPPORTED_DEVICES
from switchbot_meter_database.influx import AccessConfig, put_data

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(funcName)s %(message)s",
)


@dataclasses.dataclass
class SwitchBotCredentials:
    """SwitchBot API credentials"""

    token: str
    secret: str


class SwitchBotMeter(SwitchBot):
    """SwitchBotのうち環境センサー(temperature/humidity/lightLevel)をサポートするデバイスの継承クラス"""

    def devices(self) -> List[Device]:
        """環境センサーデバイス一覧のみを返す"""
        response = self.client.get("devices")
        return [
            Device.create(client=self.client, id=device["device_id"], **device)
            for device in response["body"]["device_list"]
            if device["device_type"] in SUPPORTED_DEVICES
        ]


def task(influxdb_access, switchbot_access, meter_devices):
    """定期実行するタスク"""
    switchbot = SwitchBotMeter(
        token=switchbot_access.token, secret=switchbot_access.secret
    )

    for device_id in meter_devices.keys():
        logger.info(f"Processing device: {device_id}")
        try:
            device = switchbot.device(device_id)
            status = device.status()
        except Exception as e:
            logging.error("Request error: %s", e)
            continue

        try:
            put_data(influxdb_access, device.type, status)
        except Exception as e:
            logging.error("Save error: %s", e)


def main():
    """CLI main function"""

    # SwitchBot credentials
    try:
        switchbot_token = os.environ["SWITCHBOT_TOKEN"]
        switchbot_secret = os.environ["SWITCHBOT_SECRET"]
    except KeyError as e:
        logging.error("Environment variable not set: %s", e)
        return

    switchbot_credentials = SwitchBotCredentials(switchbot_token, switchbot_secret)

    # Database configuration
    try:
        database = os.environ["DATABASE"]
        if database not in ["influxdb", "mongodb"]:
            logging.error("Unsupported database: %s", database)
            return
    except KeyError as e:
        logging.error("Environment variable not set: %s", e)
        return

    if database == "influxdb":
        # InfluxDB configuration
        try:
            influxdb_url = os.environ["INFLUXDB_URL"]
            influxdb_token = os.environ["INFLUXDB_TOKEN"]
            influxdb_org = os.environ["INFLUXDB_ORG"]
            influxdb_bucket = os.environ["INFLUXDB_BUCKET"]

            influxdb_config = AccessConfig(
                influxdb_url, influxdb_token, influxdb_org, influxdb_bucket
            )

        except KeyError as e:
            logging.error("Environment variable not set: %s", e)
            return
    elif database == "mongodb":
        # MongoDB configuration
        try:
            mongodb_uri = os.environ["MONGODB_URI"]
            mongodb_collection = os.environ["MONGODB_COLLECTION"]
            mongodb_user = os.environ["MONGODB_USER"]
            mongodb_password = os.environ["MONGODB_PASSWORD"]

            mongodb_config = AccessConfig(
                mongodb_uri, mongodb_collection, mongodb_user, mongodb_password
            )

        except KeyError as e:
            logging.error("Environment variable not set: %s", e)
            return

    logger.info("Start")

    switchbot = SwitchBotMeter(
        token=switchbot_credentials.token, secret=switchbot_credentials.secret
    )

    meter_devices = {}
    for device in switchbot.devices():
        meter_devices[device.id] = device.type

    logger.info("Meter devices: %s", meter_devices)

    task(influxdb_config, switchbot_credentials, meter_devices)


if __name__ == "__main__":
    main()
