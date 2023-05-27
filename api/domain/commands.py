from dataclasses import dataclass
from datetime import datetime
class Command:
    pass


@dataclass
class PutLocation(Command):
    timestamp: datetime 
    lat: float
    long: float
    accuracy: float     
    speed: float
    user_id: str


@dataclass
class HealthCheck(Command):
    pass
