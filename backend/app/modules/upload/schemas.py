from datetime import datetime

from pydantic import BaseModel


class UploadSessionOut(BaseModel):
    id: int
    user_id: int | None = None
    subject_id: int
    source_type: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceFileOut(BaseModel):
    id: int
    session_id: int
    file_name: str
    file_path: str
    file_type: str
    page_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
