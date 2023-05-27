from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from . import events


class UnableToCreateUser(Exception):
    pass


@dataclass
class Location():
    timestamp: datetime
    lat: float
    long: float
    accuracy: float
    speed: float
    user_id: str
    id: Optional[str] = None
    _events: List[events.Event] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, Location):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def append_event(self, event: events.Event):
        self._events.append(event)

    def pop_events(self) -> List[events.Event]:
        events = self._events
        self._events = []
        return events

    def __repr__(self):
        return f"<Location {self.id}>"
