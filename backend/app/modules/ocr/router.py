import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.modules.ocr import service as ocr_service
from app.modules.ocr.models import AiCorrection, OcrResult

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


@router.post("/process/{source_file_id}")
def process_file(source_file_id: int, db: Session = Depends(get_db)):
    from app.modules.upload.models import SourceFile

    sf = db.query(SourceFile).filter(SourceFile.id == source_file_id).first()
    if not sf:
        raise HTTPException(404, "文件不存在")
    result = ocr_service.process_image(db, source_file_id, sf.file_path)
    return {"ocr_result_id": result.id, "status": result.status}


@router.get("/results/{ocr_result_id}")
def get_result(ocr_result_id: int, db: Session = Depends(get_db)):
    result = db.query(OcrResult).filter(OcrResult.id == ocr_result_id).first()
    if not result:
        raise HTTPException(404, "OCR 结果不存在")

    corrections = (
        db.query(AiCorrection)
        .filter(AiCorrection.ocr_result_id == ocr_result_id)
        .all()
    )
    return {
        "ocr": {
            "id": result.id,
            "structured_data": json.loads(result.structured_data) if result.structured_data else {},
            "status": result.status,
        },
        "corrections": [
            {
                "id": c.id,
                "question_number": c.question_number,
                "question_content": c.question_content,
                "student_answer": c.student_answer,
                "is_correct": c.is_correct,
                "correct_answer": c.correct_answer,
                "error_type": c.error_type,
                "ai_analysis": json.loads(c.ai_analysis) if c.ai_analysis else {},
                "knowledge_point": c.knowledge_point,
            }
            for c in corrections
        ],
    }
