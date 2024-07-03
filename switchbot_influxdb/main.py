"""Write SwitchBot environmental sensor data to InfluxDB"""

import argparse
import dataclasses
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

# SwitchBot
SUPPORTED_DEVICES = ["Meter", "MeterPlus", "WoIOSensor", "Humidifier", "Hub 2"]
LIGHT_LEVEL_SUPPORTED_DEVICES = ["Hub 2"]


@dataclasses.dataclass
class SwitchBotAccess:
    """SwitchBot access data"""

    token: str
    secret: str


@dataclasses.dataclass
class InfluxDBAccess:
    """InfluxDB access data"""

    url: str
    token: str
    org: str
    bucket: str


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
    switchbot = SwitchBotMeter(token=switchbot_access.token, secret=switchbot_access.secret)

    for device_id in meter_devices.keys():
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

            client = InfluxDBClient(url=influxdb_access.url, token=influxdb_access.token, org=influxdb_access.org)
            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=influxdb_access.bucket, record=p)
            logging.info(f"Saved: {status}")
        except Exception as e:
            logging.error(f"Save error: {e}")


def main():
    """CLI main"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon", action="store_true", help="Daemon mode")
    parser.add_argument("-t", "--time", default=5, help="Time interval", type=int)
    parser.add_argument("--url", default=os.getenv("INFLUXDB_URL"), help="InfluxDB URL")
    parser.add_argument("--token", default=os.getenv("INFLUXDB_TOKEN"), help="InfluxDB token")
    parser.add_argument("--org", default=os.getenv("INFLUXDB_ORG"), help="InfluxDB organization")
    parser.add_argument("--bucket", default=os.getenv("INFLUXDB_BUCKET"), help="InfluxDB bucket")
    parser.add_argument("--switchbot-token", default=os.getenv("SWITCHBOT_TOKEN"), help="SwitchBot token")
    parser.add_argument("--switchbot-secret", default=os.getenv("SWITCHBOT_SECRET"), help="SwitchBot secret")
    args = parser.parse_args()

    influxdb_access = InfluxDBAccess(args.url, args.token, args.org, args.bucket)
    switchbot_access = SwitchBotAccess(args.switchbot_token, args.switchbot_secret)

    logger.info("Start")

    switchbot = SwitchBotMeter(token=switchbot_access.token, secret=switchbot_access.secret)

    meter_devices = {}
    for device in switchbot.devices():
        meter_devices[device.id] = device.type

    logger.info(f"Meter devices: {meter_devices}")

    task(influxdb_access, switchbot_access, meter_devices)
    if args.daemon:
        schedule.every(args.time).minutes.do(task, influxdb_access, switchbot_access, meter_devices)
        while True:
            schedule.run_pending()
            sleep(1)


if __name__ == "__main__":
    main()
