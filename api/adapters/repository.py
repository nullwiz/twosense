import abc
from dataclasses import asdict
from api.domain import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from motor.motor_asyncio import AsyncIOMotorClient
from api.utils.entity_factory import entity_factory
from api.domain import events
from typing import Set, Optional, TypeVar, Generic, Type

# Type declarations for MongoDB
CollectionType = AsyncIOMotorClient
# Model type declaration
T = TypeVar('T', bound=models.Entity)


# Abstract base repo
class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen: Set[models.Entity] = set()
        self.events: Set[events.Event] = set()

    async def add(self, entity: models.Entity):
        await self._add(entity)
        self.seen.add(entity)

    async def get(self, id: str) -> Optional[models.Entity]:
        entity = await self._get(id)
        if entity:
            self.seen.add(entity)
        return entity

    async def delete(self, entity: models.Entity):
        await self._delete(entity)
        self.seen.remove(entity)

    async def update(self, entity: models.Entity):
        await self._update(entity)
        self.seen.add(entity)

    @abc.abstractmethod
    async def _add(self, entity: models.Entity):
        raise NotImplementedError

    @abc.abstractmethod 
    async def _update(self, entity: models.Entity):
        raise NotImplementedError

    @abc.abstractmethod
    async def _get(self, id: str) -> Optional[models.Entity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def _delete(self, entity: models.Entity):
        raise NotImplementedError


class SqlAlchemyRepository(Generic[T], AbstractRepository):
    def __init__(self, session: AsyncSession, entity_class: Type[T]):
        super().__init__()
        self.session = session
        self.entity_class = entity_class

    async def _add(self, entity: T):
        self.session.add(entity)

    async def _get(self, id) -> Optional[T]:
        result = await self.session.execute(select(self.entity_class)
                                            .options(joinedload('*'))
                                            .filter_by(id=id))
        entity = result.scalars().one_or_none()
        if entity:
            await self.session.refresh(entity)
            self.session.expunge(entity)
        return entity
    
    async def _update(self, entity: T):
        await self.session.refresh(entity)
        entity = await self.session.merge(entity)


    async def _delete(self, entity: T):
        await self.session.delete(entity)

class MongoDBRepository(AbstractRepository):
    def __init__(self, client: CollectionType, db_name: str, collection_name: str,
                 session):
        super().__init__()
        self.collection: CollectionType = client[db_name][collection_name]
        self.session = session

    async def _add(self, location: models.Entity):
        await self.collection.insert_one(asdict(location))

    async def _get(self, id: str) -> Optional[models.Entity]:
        document = await self.collection.find_one({"id": id})
        if document:
            return entity_factory(document)

    async def _delete(self, location: models.Entity):
        await self.collection.delete_one({"id": location.id})

    async def _update(self, location: models.Entity):
        await self.collection.replace_one({"id": location.id}, asdict(location))

class AbstractUserRepository(AbstractRepository):
    @abc.abstractmethod
    async def get_by_email(self, email: str) -> Optional[models.User]:
        raise NotImplementedError

# Votes repos. 
class AbstractVoteRepository(AbstractRepository):
    pass

class SqlAlchemyVoteRepository(SqlAlchemyRepository[models.Vote],
                               AbstractVoteRepository):
    pass

class MongoVoteRepository(MongoDBRepository, AbstractVoteRepository):
    pass

# User repos.
class SqlAlchemyUserRepository(SqlAlchemyRepository[models.User],
                               AbstractUserRepository):
    async def get_by_email(self, email: str) -> Optional[models.User]:
        result = await self.session.execute(select(models.User)
                                            .filter_by(email=email))
        user = result.scalars().one_or_none()
        if user:
            await self.session.refresh(user)
            self.session.expunge(user)
        return user

class MongoUserRepository(MongoDBRepository, AbstractUserRepository):
    async def get_by_email(self, email: str) -> Optional[models.User]:
        document = await self.collection.find_one({"email": email})
        if document:
            return models.User(**document)

# Polls repos.

class AbstractPollRepository(AbstractRepository):
    pass

class SqlAlchemyPollRepository(SqlAlchemyRepository[models.Poll],
                               AbstractPollRepository):
    pass

class MongoPollRepository(MongoDBRepository, AbstractPollRepository):
    pass

# Options repos

class AbstractOptionRepository(AbstractRepository):
    pass

class SqlAlchemyOptionRepository(SqlAlchemyRepository[models.Option],
                                 AbstractOptionRepository):
     pass

class MongoOptionRepository(MongoDBRepository, AbstractOptionRepository):
    pass
