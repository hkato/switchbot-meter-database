"""Ingest SwitchBot environmental sensor data into InfluxDB or MongoDB"""

import dataclasses
import os
from typing import List

from switchbot import SwitchBot
from switchbot.devices import Device

from .devices import SUPPORTED_DEVICES
from .influxdb import InfluxDBConfig, InfluxDBWriter
from .mongodb import MongoDBConfig, MongoDBWriter


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


def task(database_writer, switchbot_access, meter_devices):
    """定期実行するタスク"""
    switchbot = SwitchBotMeter(token=switchbot_access.token, secret=switchbot_access.secret)

    for device_id in meter_devices.keys():
        print(f"Processing device: {device_id}")
        try:
            device = switchbot.device(device_id)
            status = device.status()
        except Exception as e:
            print("Request error: %s", e)
            continue

        try:
            database_writer.put_data(device.type, status)
        except Exception as e:
            print("Save error: %s", e)


def main():
    """CLI main function"""

    # SwitchBot credentials
    try:
        switchbot_token = os.environ["SWITCHBOT_TOKEN"]
        switchbot_secret = os.environ["SWITCHBOT_SECRET"]
    except KeyError as e:
        print("Environment variable not set: %s", e)
        return

    switchbot_credentials = SwitchBotCredentials(switchbot_token, switchbot_secret)

    # Database configuration
    try:
        database = os.environ["DATABASE"]
        if database not in ["influxdb", "mongodb"]:
            print("Unsupported database: %s", database)
            return
    except KeyError as e:
        print("Environment variable not set: %s", e)
        return

    if database == "influxdb":
        # InfluxDB configuration
        try:
            influxdb_url = os.environ["INFLUXDB_URL"]
            influxdb_token = os.environ["INFLUXDB_TOKEN"]
            influxdb_org = os.environ["INFLUXDB_ORG"]
            influxdb_bucket = os.environ["INFLUXDB_BUCKET"]

            database_config = InfluxDBConfig(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)

            database_writer = InfluxDBWriter()
            database_writer.config_database(database_config)

        except KeyError as e:
            print("Environment variable not set: %s", e)
            return
    elif database == "mongodb":
        # MongoDB configuration
        try:
            mongodb_uri = os.environ["MONGODB_URI"]
            mongodb_database = os.environ["MONGODB_DATABASE"]
            mongodb_collection = os.environ["MONGODB_COLLECTION"]

            database_config = MongoDBConfig(
                mongodb_uri,
                mongodb_database,
                mongodb_collection,
            )
            database_writer = MongoDBWriter()
            database_writer.config_database(database_config)

        except KeyError as e:
            print("Environment variable not set: %s", e)
            return

    print("Start")

    switchbot = SwitchBotMeter(token=switchbot_credentials.token, secret=switchbot_credentials.secret)

    # Get all meter devices
    meter_devices = {}
    for device in switchbot.devices():
        meter_devices[device.id] = device.type

    print("Meter devices: %s", meter_devices)

    # Save data to the database
    task(database_writer, switchbot_credentials, meter_devices)


if __name__ == "__main__":
    main()
