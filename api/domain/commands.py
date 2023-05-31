from dataclasses import dataclass
from datetime import datetime
#import default_factory
from dataclasses import field 
from typing import List
class Command:
    pass


# Users 
@dataclass
class CreateUser(Command):
    name : str
    last_name : str
    dni : str
    email : str
    password : str

@dataclass
class GetUser(Command):
    id: str

@dataclass
class GetUserByEmail(Command):
    email: str

@dataclass
class AuthenticateUser(Command):
    email: str
    password: str

@dataclass
class UpdateUser(Command):
    id: str
    name : str
    last_name : str
    dni : str
    email : str
    password : str

@dataclass
class ActivateUser(Command):
    id: str

@dataclass
class DeactivateUser(Command):
    id: str

@dataclass
class DeleteUser(Command):
    id: str

# Polls 
@dataclass
class CreatePoll(Command):
    id: str
    deadline : datetime
    options: List[str] = field(default_factory=list)

@dataclass
class GetPoll(Command):
    id: str

@dataclass
class UpdatePoll(Command):
    id: str
    deadline : datetime
    options: List[str] = field(default_factory=list)

@dataclass
class DeletePoll(Command):
    id: str

class GetOptionsForPoll(Command):
    id: str

# Options
@dataclass
class CreateOption(Command):
    id: str
    text: str
    id: str

@dataclass
class GetOption(Command):
    id: str


@dataclass
class UpdateOption(Command):
    id: str
    text: str
    id: str

@dataclass
class DeleteOption(Command):
    id: str

# General - Service layer
@dataclass
class CastVote(Command):
    vote: str
    timestamp: datetime
    id: str
    location: str

# General  - Healthcheck
@dataclass
class HealthCheck(Command):
    pass

