from datetime import datetime

from pydantic import BaseModel


class OcrResultOut(BaseModel):
    id: int
    source_file_id: int
    page_number: int
    raw_text: str
    structured_data: dict
    status: str
    confidence: float
    processing_time: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AiCorrectionOut(BaseModel):
    id: int
    ocr_result_id: int
    question_number: str
    question_content: str
    student_answer: str
    is_correct: bool | None
    correct_answer: str
    error_type: str
    ai_analysis: dict
    knowledge_point: str

    model_config = {"from_attributes": True}


class OcrResultWithCorrections(BaseModel):
    ocr: OcrResultOut
    corrections: list[AiCorrectionOut]
