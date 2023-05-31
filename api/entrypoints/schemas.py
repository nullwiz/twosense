from pydantic import BaseModel, Field
from datetime import datetime


class CreateUser(BaseModel):
    name: str = Field(..., description="Name of the user.")
    last_name: str = Field(..., description="Last name of the user.")
    dni: str = Field(..., description="DNI of the user.")
    email: str = Field(..., description="Email of the user.")
    password: str = Field(..., description="Password of the user.")


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email : str  |  None = None

class CastVote(BaseModel):
    vote: str = Field(..., description="The vote cast by the user.")
    timestamp: datetime = Field(..., 
                                description="Timestamp in \
                                        the local timezone of the user's device.")
    location: str = Field(..., description="Location of the user.")

class CreateOption(BaseModel):
    text: str = Field(..., description="Text of the option.")

class CreatePoll(BaseModel):
    options: list = Field(..., description="List of options.")
    deadline: datetime = Field(..., description="Deadline of the poll.")


class PutLocation(BaseModel):
    timestamp: datetime = Field(
        ..., description="Timestamp in the local timezone of the user's device.")
    lat: float = Field(..., description="Latitude of the location.")
    long: float = Field(..., description="Longitude of the location.")
    accuracy: float = Field(
        None, description="Accuracy of the location data.")
    speed: float = Field(None, description="Speed of the user.")
    id: str = Field(..., description="ID of the user.")


class ResponseData(BaseModel):
    message: str
    status_code: int


class SuccessResponse(ResponseData):
    message: str = "The data was stored successfully."
    status_code: int = 200


class ErrorResponse(ResponseData):
    message: str = "Invalid or malformatted data."
    status_code: int = 400


class ServerErrorResponse(ResponseData):
    message: str = "Any other unexpected errors."
    status_code: int = 500
