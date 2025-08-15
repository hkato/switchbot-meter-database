import dataclasses
import logging

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from switchbot_meter_database.devices import LIGHT_LEVEL_SUPPORTED_DEVICES

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AccessConfig:
    """InfluxDB access data"""

    url: str
    token: str
    org: str
    bucket: str


def put_data(influxdb_access, device_type, device_status):
    try:
        p = (
            Point(device_type)
            .tag("device_id", device_status["device_id"])
            .field("humidity", float(device_status["humidity"]))
            .field("temperature", float(device_status["temperature"]))
        )

        if device_type in LIGHT_LEVEL_SUPPORTED_DEVICES:
            p.field("light_level", int(device_status["light_level"]))

        client = InfluxDBClient(
            url=influxdb_access.url,
            token=influxdb_access.token,
            org=influxdb_access.org,
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=influxdb_access.bucket, record=p)
        logger.info("Saved: %s", device_status)

    except Exception as e:
        raise RuntimeError(f"Failed to save data to InfluxDB: {e}") from e
