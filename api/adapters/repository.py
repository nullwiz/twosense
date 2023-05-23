import abc
from api.domain import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from api.domain import events
from typing import Set


class AbstractRepository(abc.ABC):

    def __init__(self):
        self.seen: Set[models.Location] = set()
        self.events: Set[events.Event] = set()

    async def add(self, location: models.Location):
        await self._add(location)
        self.seen.add(location)

    async def get(self, id: str) -> models.Location:
        location = await self._get(id)
        if location:
            self.seen.add(location)
        return location

    async def delete(self, location: models.Location):
        await self._delete(location)
        self.seen.remove(location)

    async def get_user_id_and_timestamp(self, user_id: str,
                                        timestamp: str) -> models.Location:
        location = await self._get_user_id_and_timestamp(user_id, timestamp)
        if location:
            self.seen.add(location)
        return location

    async def get_last_location_for_user(self, user_id: str) -> models.Location:
        location = await self._get_last_location_for_user(user_id)
        if location:
            self.seen.add(location)
        return location

    async def get_location_by_timestamp(self, user_id: str,
                                        timestamp: str) -> models.Location:
        location = await self._get_location_by_timestamp(user_id, timestamp)
        if location:
            self.seen.add(location)
        return location

    @abc.abstractmethod
    async def _get_last_location_for_user(self, user_id: str) -> models.Location:
        raise NotImplementedError

    @abc.abstractmethod
    async def _add(self, location: models.Location):
        raise NotImplementedError

    @abc.abstractmethod
    async def _get(self, id: str) -> models.Location:
        raise NotImplementedError

    @abc.abstractmethod
    async def _delete(self, location: models.Location):
        raise NotImplementedError

    @abc.abstractmethod
    async def _get_user_id_and_timestamp(self, user_id: str,
                                         timestamp: str) -> models.Location:
        raise NotImplementedError

    @abc.abstractmethod
    async def _get_location_by_timestamp(self,
                                         user_id: str,
                                         timestamp: str) -> models.Location:

        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def _add(self, location: models.Location):
        self.session.add(location)

    async def _get(self, id):
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
                                         timestamp: str) -> models.Location:
        result = await self.session.execute(select(models.Location)
                                            .options(joinedload('*'))
                                            .filter_by(user_id=user_id,
                                                       timestamp=timestamp))
        location = result.scalars().one_or_none()
        if location:
            await self.session.refresh(location)
            self.session.expunge(location)
        return location

    async def _get_last_location_for_user(self, user_id: str) -> models.Location:
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
                                         timestamp: str) -> models.Location:
        result = await self.session.execute(select(models.Location)
                                            .options(joinedload('*'))
                                            .filter_by(user_id=user_id,
                                                       timestamp=timestamp))
        location = result.scalars().one_or_none()
        if location:
            await self.session.refresh(location)
            self.session.expunge(location)
        return location
