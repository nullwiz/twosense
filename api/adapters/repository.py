import abc
from dataclasses import asdict
from api.domain import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
from api.domain import events
from typing import Set, Optional, TypeVar

# Type declarations for MongoDB
CollectionType = AsyncIOMotorClient

class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen: Set[models.Location] = set()
        self.events: Set[events.Event] = set()

    async def add(self, location: models.Location):
        await self._add(location)
        self.seen.add(location)

    async def get(self, id: str) -> Optional[models.Location]:
        location = await self._get(id)
        if location:
            self.seen.add(location)
        return location

    async def delete(self, location: models.Location):
        await self._delete(location)
        self.seen.remove(location)

    async def get_user_id_and_timestamp(self, user_id: str,
                                        timestamp: str) -> Optional[models.Location]:
        location = await self._get_user_id_and_timestamp(user_id, timestamp)
        if location:
            self.seen.add(location)
        return location

    async def get_last_location_for_user(self, user_id: str) -> Optional[models.Location]:
        location = await self._get_last_location_for_user(user_id)
        if location:
            self.seen.add(location)
        return location

    async def get_location_by_timestamp(self, user_id: str,
                                        timestamp: str) -> Optional[models.Location]:
        location = await self._get_location_by_timestamp(user_id, timestamp)
        if location:
            self.seen.add(location)
        return location

    @abc.abstractmethod
    async def _get_last_location_for_user(self, user_id: str) -> Optional[models.Location]:
        raise NotImplementedError

    @abc.abstractmethod
    async def _add(self, location: models.Location):
        raise NotImplementedError

    @abc.abstractmethod
    async def _get(self, id: str) -> Optional[models.Location]:
        raise NotImplementedError

    @abc.abstractmethod
    async def _delete(self, location: models.Location):
        raise NotImplementedError

    @abc.abstractmethod
    async def _get_user_id_and_timestamp(self, user_id: str,
                                         timestamp: str) -> Optional[models.Location]:
        raise NotImplementedError

    @abc.abstractmethod
    async def _get_location_by_timestamp(self,
                                         user_id: str,
                                         timestamp: str) -> Optional[models.Location]:

        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def _add(self, location: models.Location):
        self.session.add(location)

    async def _get(self, id) -> Optional[models.Location]:
        result = await self.session.execute(select(models.Location)
                                            .options(joinedload('*'))
                                            .filter_by(id=id))
        location = result.scalars().one_or_none()
        if location:
            await self.session.refresh(location)
            self.session.expunge(location)
        return location

    async def _delete(self, location: models.Location):
        await self.session.delete(location)

    async def _get_user_id_and_timestamp(self, user_id: str,
                                         timestamp: str) -> Optional[models.Location]:
        result = await self.session.execute(select(models.Location)
                                            .options(joinedload('*'))
                                            .filter_by(user_id=user_id,
                                                       timestamp=timestamp))
        location = result.scalars().one_or_none()
        if location:
            await self.session.refresh(location)
            self.session.expunge(location)
        return location

    async def _get_last_location_for_user(self, user_id: str) -> Optional[models.Location]:
        # Get last location for user
        result = await self.session.execute(select(models.Location)
                                            .options(joinedload('*'))
                                            .filter_by(user_id=user_id)
                                            .order_by(models.Location.timestamp.desc())
                                            .limit(1))
        location = result.scalars().one_or_none()
        if location:
            await self.session.refresh(location)
            self.session.expunge(location)

        return location

    async def _get_location_by_timestamp(self, user_id: str,
                                         timestamp: str) -> Optional[models.Location]:
        result = await self.session.execute(select(models.Location)
                                            .options(joinedload('*'))
                                            .filter_by(user_id=user_id,
                                                       timestamp=timestamp))
        location = result.scalars().one_or_none()
        if location:
            await self.session.refresh(location)
            self.session.expunge(location)
        return location


class MongoDBRepository(AbstractRepository):
    def __init__(self, client: CollectionType, db_name: str, collection_name: str,
                 session):
        super().__init__()
        self.collection: CollectionType = client[db_name][collection_name]
        self.session = session

    async def _add(self, location: models.Location):
        await self.collection.insert_one(asdict(location))

    async def _get(self, id: str) -> Optional[models.Location]:
        document = await self.collection.find_one({"id": id})
        if document:
            document.pop('_id')
            return models.Location(**document)

    async def _delete(self, location: models.Location):
        await self.collection.delete_one({"id": location.id})

    async def _get_user_id_and_timestamp(self, user_id: str,
                                         timestamp: str) -> Optional[models.Location]:
        document = await self.collection.find_one({"user_id": user_id,
                                                   "timestamp": timestamp})
        if document:
            document[0].pop('_id')
            return models.Location(**document)

    async def _get_last_location_for_user(self,
                                          user_id: str) -> Optional[models.Location]:
        cursor = self.collection.find({"user_id": user_id})\
            .sort("timestamp", -1).limit(1)
        document = await cursor.to_list(length=1)
        if document:
            # Pop mongo id
            document[0].pop('_id')
            return models.Location(**document[0])

    async def _get_location_by_timestamp(self, user_id: str,
                                         timestamp: str) -> Optional[models.Location]:
        document = await self.collection.find_one({"user_id": user_id,
                                                   "timestamp": timestamp})
        if document:
            print(document)
            document.pop('_id')
            return models.Location(**document)
