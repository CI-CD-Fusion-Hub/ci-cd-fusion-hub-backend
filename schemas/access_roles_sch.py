from typing import Optional, List

from pydantic import BaseModel

from schemas.pipelines_sch import PipelineOut
from schemas.response_sch import Response
from schemas.users_sch import UserBaseOut


class CreateAccessRole(BaseModel):
    name: str
    description: str


class UpdateAccessRole(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AccessRoleBaseOut(BaseModel):
    id: int
    name: str
    description: str
    created_ts: str


class AccessRoleOut(AccessRoleBaseOut):
    members: Optional[List[UserBaseOut]] = None
    pipelines: Optional[List[PipelineOut]] = None


# Response models
class AccessRoleResponse(Response):
    data: AccessRoleOut


class AccessRolesResponse(Response):
    data: List[AccessRoleBaseOut]