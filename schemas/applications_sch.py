from typing import Optional, List

from pydantic import BaseModel, field_validator

from schemas.response_sch import Response
from utils.enums import AppType


class CreateApplication(BaseModel):
    name: str
    auth_user: str
    auth_pass: str
    base_url: str
    type: str
    status: str

    @field_validator("type", check_fields=True)
    def check_type(cls, value):
        if value in (app_type.value for app_type in AppType):
            return value
        raise ValueError(f"{value} is not a valid application type. "
                         f"Valid types are: {', '.join(app_type.value for app_type in AppType)}")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jenkins Test",
                "auth_user": "test_user",
                "auth_pass": "test_pass",
                "base_url": "https://sample.com",
                "type": "jenkins",
                "status": "active"
            }
        }


class UpdateApplication(BaseModel):
    name: Optional[str] = None
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    base_url: Optional[str] = None
    status: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jenkins Test Test",
                "auth_user": "test_user",
                "auth_pass": "test_pass",
                "base_url": "https://sample.com",
                "status": "inactive"
            }
        }


class ApplicationOut(BaseModel):
    id: int
    name: str
    auth_user: str
    auth_pass: str
    base_url: str
    type: str
    status: str
    created_ts: str


# Response models
class ApplicationResponse(Response):
    data: ApplicationOut


class ApplicationsResponse(Response):
    data: List[ApplicationOut]
