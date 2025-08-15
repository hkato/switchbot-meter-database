import dataclasses
import logging

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from switchbot_meter_database.database import DatabaseWriterBase
from switchbot_meter_database.devices import LIGHT_LEVEL_SUPPORTED_DEVICES

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class InfluxDBConfig:
    """InfluxDB configuration"""

    url: str
    token: str
    org: str
    bucket: str


class InfluxDBWriter(DatabaseWriterBase):
    def config_database(self, database_config: InfluxDBConfig):
        self.config = database_config

    def put_data(self, device_type, device_status):
        logger.info(f"Writing {device_type} to InfluxDB...")
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
                url=self.config.url,
                token=self.config.token,
                org=self.config.org,
            )
            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=self.config.bucket, record=p)
            logger.info("Saved: %s", device_status)

        except Exception as e:
            raise RuntimeError(f"Failed to save data to InfluxDB: {e}") from e
