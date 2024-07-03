import logging
import os
from time import sleep
from typing import List

import schedule
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from switchbot import SwitchBot
from switchbot.devices import Device

# Logging
formatter = "[%(levelname)-8s] %(asctime)s %(funcName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger(__name__)

# InfluxDB
url = os.environ["INFLUXDB_URL"]
token = os.environ["INFLUXDB_TOKEN"]
org = os.environ["INFLUXDB_ORG"]
bucket = os.environ["INFLUXDB_BUCKET"]
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

# SwitchBot
ACCESS_TOKEN: str = os.environ["SWITCHBOT_ACCESS_TOKEN"]
SECRET: str = os.environ["SWITCHBOT_SECRET"]
SUPPORTED_DEVICES = ["Meter", "MeterPlus", "WoIOSensor", "Humidifier", "Hub 2"]
LIGHT_LEVEL_SUPPORTED_DEVICES = ["Hub 2"]


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


def get_meter_devices() -> dict:
    """環境センサーを持つデバイスの一覧を取得"""
    switchbot = SwitchBotMeter(token=ACCESS_TOKEN, secret=SECRET)

    meter_devices = {}
    for device in switchbot.devices():
        meter_devices[device.id] = device.type

    logger.info(f"Meter devices: {meter_devices}")

    return meter_devices


def task(devices):
    """定期実行するタスク"""
    switchbot = SwitchBotMeter(token=ACCESS_TOKEN, secret=SECRET)

    for device_id in devices.keys():
        device = switchbot.device(device_id)
        try:
            status = device.status()
        except Exception as e:
            logging.error(f"Request error: {e}")
            continue

        try:
            p = (
                Point(device.type)
                .tag("device_id", status["device_id"])
                .field("humidity", float(status["humidity"]))
                .field("temperature", float(status["temperature"]))
            )

            if device.type in LIGHT_LEVEL_SUPPORTED_DEVICES:
                p.field("light_level", int(status["light_level"]))

            write_api.write(bucket=bucket, record=p)
            logging.info(f"Saved: {status}")
        except Exception as e:
            logging.error(f"Save error: {e}")


if __name__ == "__main__":
    devices = get_meter_devices()

    schedule.every(5).minutes.do(task, devices)

    while True:
        schedule.run_pending()
        sleep(1)
