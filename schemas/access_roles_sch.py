from typing import Optional

from pydantic import BaseModel


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
    members: Optional[list] = None
    pipelines: Optional[list] = None
