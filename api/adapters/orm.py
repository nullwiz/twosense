from sqlalchemy.orm import registry
from sqlalchemy import Column, String, DateTime
from sqlalchemy import ForeignKey, Table, event, Boolean
from sqlalchemy import Integer
from api.domain import models
import logging

logger = logging.getLogger(__name__)

mapper_registry = registry()

metadata = mapper_registry.metadata

users = Table(
    "users", 
    metadata,
    Column("id", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
    Column("last_name", String(70), nullable=False),
    Column("dni", String(12), nullable=False),
    Column("email", String(50), nullable=False),
    Column("password", String(120), nullable=False),
    Column("active", Boolean(), nullable=False, default=False),
    Column("created_at", DateTime()),
    Column("updated_at", DateTime()),
)

polls = Table(
    "polls",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("options", String(300), nullable=True),
    Column("deadline", DateTime()),
    Column("created_at", DateTime()),
    Column("updated_at", DateTime()),
)

votes = Table(
    "votes",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("vote", String(50), nullable=False),
    Column("user_id", ForeignKey('users.id'), nullable=False),
    Column("poll_id", ForeignKey('polls.id'), nullable=False),
    Column("created_at", DateTime()),
    Column("updated_at", DateTime()),
)

options = Table(
        "options",
        metadata,
        Column("id", String(50), primary_key=True),
        Column("text", String(50), nullable=False),
        Column("votes", Integer(), nullable=False),
        Column("poll_id", ForeignKey('polls.id'), nullable=False),
        Column("created_at", DateTime()),
        Column("updated_at", DateTime()),
)


def start_mappers():
    logger.info("Starting mappers")
    mapper_registry.map_imperatively(models.User, users)
    mapper_registry.map_imperatively(models.Poll, polls)
    mapper_registry.map_imperatively(models.Vote, votes)
    mapper_registry.map_imperatively(models.Option, options)
    logger.info("Mappers started")

def create_tables(engine):
    logger.info("Creating tables")
    metadata.create_all(engine)
    logger.info("Tables created")

def drop_tables(engine):
    logger.info("Dropping tables")
    metadata.drop_all(engine)
    logger.info("Tables dropped")

def has_started_mappers():
    return len(mapper_registry.mappers) > 0

@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
    for event_ in user.events:
        user.events.append(event_)
    user._events = []
