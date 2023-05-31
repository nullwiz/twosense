from dataclasses import dataclass
from datetime import date


class Event:
    pass


@dataclass
class LocationAdded(Event):
    timestamp: date
    lat: float
    long: float
    accuracy: float
    speed: float
    user_id: str
