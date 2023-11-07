from typing import Optional, List, Dict

from pydantic import BaseModel

from schemas.pipelines_sch import PipelineOut
from schemas.response_sch import Response


class Pipeline(BaseModel):
    id: int
    name: str


class CreateUsersRequest(BaseModel):
    user_id: Optional[int]
    message: str
    pipelines: List[Pipeline]

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "message": "Test msg",
                "pipelines": [{}]
            }
        }


class UpdateUsersRequest(BaseModel):
    status: Optional[str]
    message: Optional[str]
    pipelines: Optional[List[Pipeline]] = None


class UsersRequestBaseOut(BaseModel):
    id: int
    status: str
    message: str
    created_ts: str


class UsersRequestOut(UsersRequestBaseOut):
    pipelines: List | None


# Response models
class UsersRequestResponse(Response):
    data: UsersRequestBaseOut


class UsersRequestsResponse(Response):
    data: List[UsersRequestBaseOut]
