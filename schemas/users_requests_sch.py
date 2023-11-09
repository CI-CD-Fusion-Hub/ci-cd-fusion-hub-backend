from typing import Optional, List

from pydantic import BaseModel, field_validator

from schemas.response_sch import Response
from utils.enums import RequestStatus


class Pipeline(BaseModel):
    id: int
    name: str


class User(BaseModel):
    id: int
    email: str


class CreateUsersRequest(BaseModel):
    user_id: Optional[int] = None
    message: str
    pipelines: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "message": "Test msg",
                "pipelines": []
            }
        }


class UpdateUsersRequest(BaseModel):
    status: Optional[str]
    message: Optional[str]
    pipelines: Optional[List[int]] = None

    @field_validator("status", check_fields=True)
    def validate_status(cls, status: str) -> str:
        """Validates that status is 'pending', 'canceled', 'declined' or 'completed'."""
        if status in (us.value for us in RequestStatus):
            return status
        raise ValueError(
            f"Invalid status {status}. Please, provide valid status {', '.join(us.value for us in RequestStatus)}.")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "message": "Test msg",
                "pipelines": []
            }
        }


class UsersRequestBaseOut(BaseModel):
    id: int
    status: str
    message: str
    created_ts: str


class UsersRequestOut(UsersRequestBaseOut):
    user: Optional[User]
    pipelines: List


# Response models
class UsersRequestResponse(Response):
    data: UsersRequestBaseOut


class UsersRequestsResponse(Response):
    data: List[UsersRequestBaseOut]
