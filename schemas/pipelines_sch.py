from pydantic import BaseModel


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


class GitlabStartPipelineParams(BaseModel):
    class Config:
        json_schema_extra = {
            "parameters": {
                "branch": "main"
            }
        }
        extra = "allow"


