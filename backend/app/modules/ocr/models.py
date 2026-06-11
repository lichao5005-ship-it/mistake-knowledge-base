from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.shared.database import Base


class OcrResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True)
    source_file_id = Column(Integer, ForeignKey("source_files.id"))
    page_number = Column(Integer, default=1)
    raw_text = Column(Text, default="")
    structured_data = Column(Text, default="")  # JSON: 逐题结构化数据
    status = Column(String(20), default="pending")  # pending / done / failed
    confidence = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)


class AiCorrection(Base):
    __tablename__ = "ai_corrections"

    id = Column(Integer, primary_key=True)
    ocr_result_id = Column(Integer, ForeignKey("ocr_results.id"))
    question_number = Column(String(20))
    question_content = Column(Text, default="")
    student_answer = Column(Text, default="")
    is_correct = Column(Boolean, nullable=True)
    correct_answer = Column(Text, default="")
    error_type = Column(String(50), default="")  # 粗心/概念不清/审题错误/计算错误/未作答
    ai_analysis = Column(Text, default="")  # JSON: 解题思路
    knowledge_point = Column(String(100), default="")
