"""Write SwitchBot environmental sensor data to InfluxDB"""

import argparse
import dataclasses
import logging
import os
from typing import List

from switchbot import SwitchBot
from switchbot.devices import Device

from switchbot_meter_influxdb.devices import SUPPORTED_DEVICES
from switchbot_meter_influxdb.influx import AccessConfig, save_influx
from switchbot_meter_influxdb.logger import set_logger

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SwitchBotAccess:
    """SwitchBot access data"""

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
            save_influx(influxdb_access, device.type, status)
        except Exception as e:
            logging.error("Save error: %s", e)


def main():
    """CLI main"""
    parser = argparse.ArgumentParser()
    # parser.add_argument("-d", "--daemon", action="store_true", help="Daemon mode")
    # parser.add_argument("-t", "--time", default=5, help="Time interval", type=int)
    parser.add_argument("--url", default=os.getenv("INFLUXDB_URL"), help="InfluxDB URL")
    parser.add_argument(
        "--token", default=os.getenv("INFLUXDB_TOKEN"), help="InfluxDB token"
    )
    parser.add_argument(
        "--org", default=os.getenv("INFLUXDB_ORG"), help="InfluxDB organization"
    )
    parser.add_argument(
        "--bucket", default=os.getenv("INFLUXDB_BUCKET"), help="InfluxDB bucket"
    )
    parser.add_argument(
        "--switchbot-token",
        default=os.getenv("SWITCHBOT_TOKEN"),
        help="SwitchBot token",
    )
    parser.add_argument(
        "--switchbot-secret",
        default=os.getenv("SWITCHBOT_SECRET"),
        help="SwitchBot secret",
    )
    args = parser.parse_args()

    influxdb_access = AccessConfig(args.url, args.token, args.org, args.bucket)
    switchbot_access = SwitchBotAccess(args.switchbot_token, args.switchbot_secret)

    logger.info("Start")

    switchbot = SwitchBotMeter(
        token=switchbot_access.token, secret=switchbot_access.secret
    )

    meter_devices = {}
    for device in switchbot.devices():
        meter_devices[device.id] = device.type

    logger.info("Meter devices: %s", meter_devices)

    task(influxdb_access, switchbot_access, meter_devices)


if __name__ == "__main__":
    set_logger()
    main()
