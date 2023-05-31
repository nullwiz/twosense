import uuid
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
from . import events


class UnableToCreateUser(Exception):
    pass


@dataclass
class Entity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _events: List[events.Event] = field(default_factory=list)

    def append_event(self, event: events.Event):
        self._events.append(event)

    def pop_events(self) -> List[events.Event]:
        events = self._events
        self._events = []
        return events

@dataclass
class Vote(Entity):
    vote: str = field(default_factory=str)
    user_id: str = field(default_factory=str)
    location: str = field(default_factory=str)


@dataclass
class Poll(Entity):
    deadline: datetime = field(default_factory=datetime.utcnow)
    options: List[str] = field(default_factory=list)


@dataclass
class Option(Entity):
    text: str = field(default_factory=str)
    votes: int = 0 
    poll_id: str = field(default_factory=str)


@dataclass
class User(Entity):
    name: str = field(default_factory=str)
    last_name: str = field(default_factory=str)
    dni: str = field(default_factory=str)
    email: str = field(default_factory=str)
    password: str = field(default_factory=str)
    active: bool = False
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<User {self.id}>"

