from sqlalchemy.orm import registry
from api.domain import models
from sqlalchemy import Column, String, Float
from sqlalchemy import DateTime, Table, event
import logging

logger = logging.getLogger(__name__)

mapper_registry = registry()

metadata = mapper_registry.metadata

location = Table(
    "locations",
    metadata,
    Column("timestamp", DateTime()),
    Column("id", String(50), primary_key=True),
    Column("lat", Float(), nullable=False),
    Column("long", Float(), nullable=False),
    Column("accuracy", Float(), nullable=False),
    Column("speed", Float(), nullable=False),
    Column("user_id", String(50)),
)


def start_mappers():
    logger.info("Starting mappers")
    mapper_registry.map_imperatively(models.Location, location)
    logger.info("Mappers started")


def create_tables(engine):
    logger.info("Creating tables")
    metadata.create_all(engine)
    logger.info("Tables created")


def drop_tables(engine):
    logger.info("Dropping tables")
    metadata.drop_all(engine)
    logger.info("Tables dropped")


@event.listens_for(models.Location, "load")
def receive_load(location, _):
    location.events = []
    for event_ in location.events:
        location.events.append(event_)
    location._events = []
