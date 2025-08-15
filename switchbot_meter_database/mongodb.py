import dataclasses
import logging

from switchbot_meter_database.database import DatabaseWriterBase
from switchbot_meter_database.devices import LIGHT_LEVEL_SUPPORTED_DEVICES

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MongoDBConfig:
    """MongoDB configuration"""

    uri: str
    collection: str
    username: str
    password: str


class MongoDBWriter(DatabaseWriterBase):
    def config_database(self, database_config: MongoDBConfig):
        self.config = database_config

    def put_data(self, device_type, device_status):
        logger.info(f"Writing {device_type} to MongoDB...")
        try:
            logger.info("Saved: %s", device_status)
        except Exception as e:
            raise RuntimeError(f"Failed to save data to MongoDB: {e}") from e
