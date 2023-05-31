from pymongo import MongoClient
from api.config import get_mongo_connection_string
from api.config import get_mongo_collection
from logging import getLogger

logger = getLogger(__name__)
mongo_db = get_mongo_collection() 
client = MongoClient(get_mongo_connection_string())
logger.info("Connecting to mongo client")
db = client[mongo_db]

users_schema ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "name", "last_name", "dni", "email", "password", "active", "created_at", "updated_at"],
        "properties": {
            "id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "last_name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "dni": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "active": {
                "bsonType": "bool",
                "description": "must be a boolean and is required"
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
        }
    }
} 


poll_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "options", "deadline", "created_at", "updated_at"],
        "properties": {
            "id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "options": {
                "bsonType": "string",
                "description": "must be a string"
            },
            "deadline": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
        }
    }
}


vote_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "vote", "user_id", "poll_id", "created_at", "updated_at"],
        "properties": {
            "id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "vote": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "user_id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "poll_id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
        }
    }
}

option_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "text", "votes", "poll_id", "created_at", "updated_at"],
        "properties": {
            "id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "text": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "votes": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "poll_id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "must be a date and is required"
            },
        }
    }
    }


def drop_collections():
    logger.info("Dropping collections")
    db.users.drop()
    db.polls.drop()
    db.votes.drop()
    db.options.drop()
    logger.info("Collections dropped")


# Create collection with validator schema
def create_collections():
    logger.info("Creating collections")
    db.create_collection("users", validator=users_schema)
    db.create_collection("polls", validator=poll_schema)
    db.create_collection("options", validator=option_schema)
    db.create_collection("votes", validator=vote_schema)
    logger.info("Collections created")

if __name__ == "__main__":
    drop_collections()
    create_collections()
