from pydantic import BaseModel


class SubjectOut(BaseModel):
    id: int
    name: str
    icon: str

    model_config = {"from_attributes": True}


class KnowledgePointOut(BaseModel):
    id: int
    subject_id: int
    name: str
    parent_id: int | None = None
    level: int

    model_config = {"from_attributes": True}
