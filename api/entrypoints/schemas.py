from pydantic import BaseModel, Field
from datetime import datetime


class PutLocation(BaseModel):
    timestamp: datetime = Field(
        ..., description="Timestamp in the local timezone of the user's device.")
    lat: float = Field(..., description="Latitude of the location.")
    long: float = Field(..., description="Longitude of the location.")
    accuracy: float = Field(
        None, description="Accuracy of the location data.")
    speed: float = Field(None, description="Speed of the user.")
    user_id: str = Field(..., description="ID of the user.")


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
