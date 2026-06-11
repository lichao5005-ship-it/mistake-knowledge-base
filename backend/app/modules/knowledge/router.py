from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.modules.knowledge import service, schemas
from app.shared.database import get_db

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/subjects", response_model=list[schemas.SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return service.get_subjects(db)


@router.get("/subjects/{subject_id}/points", response_model=list[schemas.KnowledgePointOut])
def list_knowledge_points(subject_id: int, db: Session = Depends(get_db)):
    return service.get_knowledge_points(db, subject_id)
