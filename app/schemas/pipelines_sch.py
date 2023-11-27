from typing import List

from pydantic import BaseModel

from app.schemas.response_sch import Response


class PipelineApplicationOut(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        extra = "ignore"


class PipelineOut(BaseModel):
    id: int
    name: str
    application: PipelineApplicationOut


# Response models
class PipelineResponse(Response):
    data: PipelineOut


class PipelinesResponse(Response):
    data: List[PipelineOut]


class GitlabStartPipelineParams(BaseModel):
    class Config:
        json_schema_extra = {
            "branch": "main"
        }
        extra = "allow"


class JenkinsStartPipelineParams(BaseModel):
    class Config:
        json_schema_extra = {
            "parameters": {
                "branch": "main"
            }
        }
        extra = "allow"


class GithubStartPipelineParams(BaseModel):
    class Config:
        json_schema_extra = {
            "branch": "main"
        }
        extra = "allow"
