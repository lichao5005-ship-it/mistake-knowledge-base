import json
import time
from pathlib import Path

from sqlalchemy.orm import Session

from app.shared.ai_client import call_qwen_text, call_qwen_vision
from app.modules.ocr.models import AiCorrection, OcrResult
from app.modules.ocr.prompts import CORRECTION_PROMPT, OCR_PROMPT


def process_image(db: Session, source_file_id: int, image_path: str) -> OcrResult:
    """处理一张图片：OCR → 逐题判错 → 返回结果"""
    t0 = time.time()
    image_bytes = Path(image_path).read_bytes()

    # Step 1: OCR 识别
    ocr_raw = call_qwen_vision(OCR_PROMPT, image_bytes)
    ocr_data = json.loads(ocr_raw)
    t1 = time.time()

    result = OcrResult(
        source_file_id=source_file_id,
        raw_text=ocr_raw,
        structured_data=json.dumps(ocr_data, ensure_ascii=False),
        status="done",
        confidence=0.9,
        processing_time=t1 - t0,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    # Step 2: 逐题判错
    for q in ocr_data.get("questions", []):
        if not q.get("student_answer"):
            # 未作答
            correction = AiCorrection(
                ocr_result_id=result.id,
                question_number=q["number"],
                question_content=q["content"],
                student_answer="",
                is_correct=False,
                error_type="未作答",
                correct_answer="",
                ai_analysis="",
                knowledge_point="",
            )
            db.add(correction)
            continue

        prompt = CORRECTION_PROMPT.format(
            question_content=q["content"],
            student_answer=q["student_answer"],
        )
        correction_raw = call_qwen_text(prompt)
        correction_data = json.loads(correction_raw)

        correction = AiCorrection(
            ocr_result_id=result.id,
            question_number=q["number"],
            question_content=q["content"],
            student_answer=q["student_answer"],
            is_correct=correction_data["is_correct"],
            correct_answer=correction_data["correct_answer"],
            error_type=correction_data["error_type"],
            ai_analysis=json.dumps(correction_data, ensure_ascii=False),
            knowledge_point=correction_data.get("knowledge_point", ""),
        )
        db.add(correction)

    db.commit()
    return result
