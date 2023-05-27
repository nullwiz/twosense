import os
from motor.motor_asyncio import AsyncIOMotorClient

MongoDBClient = AsyncIOMotorClient

def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432
    password = os.environ.get("DB_PASSWORD", "password")
    user, db_name = "postgres", "locations"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

# For creating initial tables. not used in docker


def get_sync_postgres_uri():
    host = "127.0.0.1"
    port = 5432
    password = os.environ.get("DB_PASSWORD", "password")
    user, db_name = "postgres", "locations"
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = 6379
    return {"host": host, "port": port}


def get_repo_orm():
    return 'sqlalchemy'


def get_mongo_db():
    return 'locations'

def get_mongo_collection():
    return 'locations'

# Default mongoclient is AsyncIOMotorClient
def get_mongo_client():
    host = os.environ.get("MONGO_HOST", "localhost")
    port = 27017
    return MongoDBClient(f"mongodb://{host}:{port}/")

def get_mongo_connection_string():
    host = os.environ.get("MONGO_HOST", "localhost")
    port = 27017
    return f"mongodb://{host}:{port}/"


def mongo_config():
    # Mongo config returns AsyncIO client and database
    DEFAULT_CLIENT = get_mongo_client()
    DEFAULT_DB = DEFAULT_CLIENT[get_mongo_db()]
    return { "client": DEFAULT_CLIENT, "db": DEFAULT_DB, 
            "collection": get_mongo_collection(), 
            "connection_string": get_mongo_connection_string()} 
