from typing import List

from pydantic import BaseModel, field_validator
from schemas.users_sch import ValidatorUtils
from utils.enums import AuthMethods


class LoginUser(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def email_check(cls, email):
        return ValidatorUtils.validate_email(email)


class CreateAuthMethod(BaseModel):
    type: str
    properties: dict = {}
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
