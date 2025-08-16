"""MongoDB connection and data writing module."""

import dataclasses
import logging
from datetime import datetime, timezone

from pymongo import MongoClient

from switchbot_meter_database.database import DatabaseWriterBase
from switchbot_meter_database.devices import LIGHT_LEVEL_SUPPORTED_DEVICES

logger = logging.getLogger(__name__)

# MongoDB timeseries collection options
TIMESERIES_OPTIONS = {
    "timeField": "timestamp",
    "metaField": "device_id",
    "granularity": "seconds",
}
# MongoDB TTL index options
TTL_SECONDS = 10 * 365 * 24 * 3600  # 10 years


@dataclasses.dataclass
class MongoDBConfig:
    """MongoDB configuration"""

    uri: str
    database: str
    collection: str
    username: str
    password: str


class MongoDBWriter(DatabaseWriterBase):
    """MongoDB writer class"""

    def config_database(self, database_config: MongoDBConfig):
        """Configure the MongoDB database connection."""

        self.config = database_config

        self.client = MongoClient(
            self.config.uri,
            username=self.config.username,
            password=self.config.password,
        )

        self.database = self.client[self.config.database]

        if self.config.collection not in self.database.list_collection_names():
            logger.info(
                f"Creating collection {self.config.collection} in database {self.database.name}"
            )
            self.database.create_collection(
                self.config.collection,
                timeseries=TIMESERIES_OPTIONS,
                expireAfterSeconds=TTL_SECONDS,
            )

        self.collection = self.database[self.config.collection]

    def put_data(self, device_type, device_status):
        """Write device status data to MongoDB."""

        logger.info(f"Writing {device_type} to MongoDB...")
        logger.info("Device status: %s", device_status)

        try:
            timestamp = datetime.now(timezone.utc)
            doc = {
                "timestamp": timestamp,
                "metadata": {"device_id": device_status["device_id"]},
                "temperature": float(device_status["temperature"]),
                "humidity": float(device_status["humidity"]),
            }
            if device_type in LIGHT_LEVEL_SUPPORTED_DEVICES:
                doc["light_level"] = int(device_status["light_level"])

            self.collection.insert_one(doc)

            logger.info("Saved: %s", doc)
        except Exception as e:
            raise RuntimeError(f"Failed to save data to MongoDB: {e}") from e
