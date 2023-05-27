from __future__ import annotations
import abc
import api.config as config
from api.adapters import repository
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection
from motor.motor_asyncio import AsyncIOMotorDatabase

MongoDBClient = AsyncIOMotorClient


class AbstractUnitOfWork(abc.ABC):
    locations: repository.AbstractRepository

    async def __aenter__(self) -> AbstractUnitOfWork:
        return self

    async def __aexit__(self, *args):
        await self._rollback()

    async def commit(self):
        await self._commit()

    def collect_new_events(self):
        for loc in self.locations.seen:
            while loc._events:
                yield loc._events.pop(0)

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def _rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def __repr__(self):
        raise NotImplementedError


def create_engine():
    return create_async_engine(
        config.get_postgres_uri(),
        future=True,
        echo=True,
    )


DEFAULT_SESSION_FACTORY = async_sessionmaker(
    create_engine(),
    expire_on_commit=False,
    class_=AsyncSession,
    future=True,
)

MONGO_CONFIG = config.mongo_config()


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.locations = repository.SqlAlchemyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def _rollback(self):
        await self.session.rollback()

    async def __repr__(self):
        return f"<SqlAlchemyUnitOfWork(session={self.session})>"


# class MongoDBUnitOfWork(AbstractUnitOfWork):
# def __init__(self, db: MongoDBClient = MONGO_CONFIG["client"]):
# self.db = db
##
# async def __aenter__(self):
# self.session = await self.db.start_session()
# self.session.start_transaction()
# self.locations = repository.MongoDBRepository(self.db,
# MONGO_CONFIG["collection"],
# MONGO_CONFIG["collection"],
# self.session)
# return await super().__aenter__()
##
# async def __aexit__(self, *args):
# await super().__aexit__(*args)
# await self.session.end_session()
##
# async def _commit(self):
# await self.session.commit_transaction()
##
# async def _rollback(self):
# await self.session.abort_transaction()
##
# async def __repr__(self):
# return f"<MongoDBUnitOfWork(db={self.db})>"
##

class MongoDBUnitOfWork(AbstractUnitOfWork):
    def __init__(self, client: MongoDBClient = MONGO_CONFIG["client"],
                 db_name: str = "locations", collection_name: str = "locations"):
        self.client = client
        self.db_name = db_name
        self.collection_name = collection_name
        self.session = None
        self.transaction_started = False

    async def __aenter__(self):
        self.session = await self.client.start_session()
        self.session.start_transaction()
        self.transaction_started = True
        self.locations = repository.MongoDBRepository(self.client, self.db_name,
                                                      self.collection_name, self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:  # An error occurred
            if self.transaction_started:
                await self.session.abort_transaction()
                self.transaction_started = False
        else:
            if self.transaction_started:
                await self.session.commit_transaction()
                self.transaction_started = False

        await self.session.end_session()

    async def _commit(self):
        if self.transaction_started:
            await self.session.commit_transaction()
            self.transaction_started = False

    async def _rollback(self):
        if self.transaction_started:
            await self.session.abort_transaction()
            self.transaction_started = False

    async def __repr__(self):
        return f"<MongoDBUnitOfWork(db={self.db})>"
