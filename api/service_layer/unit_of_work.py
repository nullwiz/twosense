from __future__ import annotations
import abc
import api.config as config
from api.adapters import repository
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker


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
