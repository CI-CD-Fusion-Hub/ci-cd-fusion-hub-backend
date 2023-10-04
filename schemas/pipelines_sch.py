from pydantic import BaseModel


class PipelineOut(BaseModel):
    id: int
    name: str
    application: dict
