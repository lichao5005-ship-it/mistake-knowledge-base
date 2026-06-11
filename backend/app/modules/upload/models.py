from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.shared.database import Base


class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    source_type = Column(String(20), default="photo")  # photo / file
    status = Column(String(20), default="pending")      # pending / processing / done
    created_at = Column(DateTime, default=datetime.now)


class SourceFile(Base):
    __tablename__ = "source_files"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("upload_sessions.id"))
    file_name = Column(String(200))
    file_path = Column(Text)
    file_type = Column(String(20))  # jpg / png / pdf / docx
    page_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
