import datetime
import re
from typing import Optional, List

from pydantic import BaseModel, validator

from schemas.pipelines_sch import PipelineOut


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "asd",
                "last_name": "CH",
                "email": "test1@gmail.com",
                "password": "asdf@asdf",
                "confirm_password": "asdf@asdf"
            }
        }

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        if "password" in values and confirm_password != values["password"]:
            raise ValueError("password and confirm_password do not match")
        return confirm_password

    @validator("status")
    def status_check(cls, status):
        """Validates that status is 'active' or 'inactive'"""
        status_list = ["active", "inactive"]
        if status not in status_list:
            raise ValueError(
                f"Invalid status {status}. Please, provide valid status {status_list}.")

        return status

    @validator("email")
    def email_check(cls, email):
        """
        The regular expression pattern \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b matches any email address.
        The \b word boundary anchor ensures that the pattern matches only complete words. The [A-Za-z0-9._%+-]+ character
        class matches one or more occurrences of any alphanumeric character, dot, underscore, percent sign, plus sign or
        hyphen. The @[A-Za-z0-9.-]+ matches the at symbol and one or more occurrences of any alphanumeric character,
        dot or hyphen. The \.[A-Z|a-z]{2,} matches a dot followed by two or more occurrences of any uppercase or lowercase
        letter.
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise ValueError(
                f"Invalid email address {repr(email)}. Please, try again with different email.")
        return email


class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    status: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "asd",
                "last_name": "CH",
                "email": "test1@gmail.com",
                "password": "asdf@asdf",
                "confirm_password": "asdf@asdf"
            }
        }

    @validator("email")
    def email_check(cls, email):
        """
        The regular expression pattern \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b matches any email address.
        The \b word boundary anchor ensures that the pattern matches only complete words. The [A-Za-z0-9._%+-]+ character
        class matches one or more occurrences of any alphanumeric character, dot, underscore, percent sign, plus sign or
        hyphen. The @[A-Za-z0-9.-]+ matches the at symbol and one or more occurrences of any alphanumeric character,
        dot or hyphen. The \.[A-Z|a-z]{2,} matches a dot followed by two or more occurrences of any uppercase or lowercase
        letter.
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise ValueError(
                f"Invalid email address {repr(email)}. Please, try again with different email.")
        return email

    @validator("confirm_password", pre=True, always=True)
    def check_passwords_match(cls, confirm_password, values):
        if 'password' in values and values['password'] is not None:
            if confirm_password is None:
                raise ValueError("confirm_password must be set if password is set")
            if confirm_password != values['password']:
                raise ValueError("password and confirm_password do not match")
        return confirm_password

    @validator("status")
    def status_check(cls, status):
        """Validates that status is 'active' or 'inactive'"""
        status_list = ["active", "inactive"]
        if status not in status_list:
            raise ValueError(
                f"Invalid status {status}. Please, provide valid status {status_list}.")

        return status

class UserBaseOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    status: str
    created_ts: str


class UserOut(UserBaseOut):
    roles: Optional[list] = []
    pipelines: Optional[List[PipelineOut]] = []


class LoginUser(BaseModel):
    email: str
    password: str
