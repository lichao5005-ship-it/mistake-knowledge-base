from sqlalchemy.orm import Session

from app.modules.knowledge.models import KnowledgePoint, Subject


def get_subjects(db: Session) -> list[Subject]:
    return db.query(Subject).order_by(Subject.sort_order).all()


def get_knowledge_points(db: Session, subject_id: int) -> list[KnowledgePoint]:
    return (
        db.query(KnowledgePoint)
        .filter(KnowledgePoint.subject_id == subject_id)
        .order_by(KnowledgePoint.level, KnowledgePoint.sort_order)
        .all()
    )
