from pymongo import MongoClient
from api.config import get_mongo_connection_string
from api.config import get_mongo_collection
from logging import getLogger

logger = getLogger(__name__)
mongo_db = get_mongo_collection() 
client = MongoClient(get_mongo_connection_string())
logger.info("Connecting to mongo client")
db = client[mongo_db]

schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["timestamp", "id", "lat", "long", "accuracy", "speed", "user_id"],
            "properties": {
                "timestamp": {
                    "bsonType": "date",
                    "description": "must be a date and is required"
                },
                "id": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "lat": {
                    "bsonType": "double",
                    "description": "must be a double and is required"
                },
                "long": {
                    "bsonType": "double",
                    "description": "must be a double and is required"
                },
                "accuracy": {
                    "bsonType": "double",
                    "description": "must be a double and is required"
                },
                "speed": {
                    "bsonType": "double",
                    "description": "must be a double and is required"
                },
                "user_id": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                }
            }
        }
    }
def drop_collections():
    logger.info("Dropping collections")
    db.locations.drop()
    logger.info("Collections dropped")


# Create collection with validator schema
def create_collections():
    logger.info("Creating collections")
    db.create_collection("locations", validator=schema)
    logger.info("Collections created")

if __name__ == "__main__":
    drop_collections()
    create_collections()
