from dataclasses import dataclass


class Command:
    pass


@dataclass
class PutLocation(Command):
    timestamp: str
    lat: float
    long: float
    accuracy: float
    speed: float
    user_id: str


@dataclass
class HealthCheck(Command):
    pass
