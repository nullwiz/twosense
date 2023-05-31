from dataclasses import dataclass
from datetime import date


class Event:
    pass


@dataclass
class UserCreated(Event):
    user_id: str
    name : str
    last_name : str
    dni : str
    email : str
    password : str

@dataclass
class PollAdded(Event):
    pass

@dataclass
class VoteReceived(Event):
    pass 

