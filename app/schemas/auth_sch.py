from typing import List

from pydantic import BaseModel, field_validator
from app.schemas.users_sch import ValidatorUtils
from app.utils.enums import AuthMethods


class LoginUser(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def email_check(cls, email):
        return ValidatorUtils.validate_email(email)


class AADProperties(BaseModel):
    aad_client_id: str
    aad_client_secret: str
    aad_tenant_id: str
    aad_scope: list

    class Config:
        json_schema_extra = {
            "example": {
                "aad_client_id": "asdfg-asdfasdfas",
                "aad_client_secret": "12089-34712hjaspdojkfhasd9f80",
                "aad_tenant_id": "opsiadhjfga89sd7fy0as9dufhjas",
                "aad_scope": [
                    "https://graph.microsoft.com/.default"
                ]
            }
        }


class CASProperties(BaseModel):
    cas_server_url: str
    cas_version: int
    cas_verify_ssl: bool

    @field_validator("cas_verify_ssl")
    def validate_cas_verify_ssl(cls, value):
        if not isinstance(value, bool):
            raise ValueError("cas_verify_ssl must be a boolean value")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "cas_server_url": "https://cas.domain/login",
                "cas_version": 3,
                "cas_verify_ssl": False
            }
        }


class LocalProperties(BaseModel):
    pass


class CreateAuthMethod(BaseModel):
    type: str
    properties: CASProperties | AADProperties | LocalProperties = {}
    admin_users: List[str]

    @field_validator("type")
    def validate_status(cls, type: str) -> str:
        """Validates that status is 'ADDS', 'CAS' or 'Local'."""
        if type in (am.value for am in AuthMethods):
            return type
        raise ValueError(
            f"Invalid type {type}. Please, provide valid type {', '.join(us.value for us in AuthMethods)}.")


class AuthOut(BaseModel):
    id: int
    type: str
    properties: dict = {}
    admin_users: List[str] = []
