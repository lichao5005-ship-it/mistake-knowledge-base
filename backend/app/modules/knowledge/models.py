from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.shared.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(20), default="")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)

    parent = relationship("KnowledgePoint", remote_side="KnowledgePoint.id", backref="children")
