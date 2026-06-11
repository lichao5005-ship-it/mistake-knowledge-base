from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.modules.upload import service as upload_service

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/session")
def create_session(
    subject_id: int = Form(...),
    user_id: int = Form(1),
    db: Session = Depends(get_db),
):
    session = upload_service.create_session(db, user_id, subject_id)
    return {"session_id": session.id, "subject_id": subject_id}


@router.post("/files")
async def upload_files(
    session_id: int = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    results = []
    for f in files:
        sf = await upload_service.save_upload_file(db, session_id, f)
        results.append({"file_id": sf.id, "file_name": sf.file_name})
    return {"session_id": session_id, "files": results}
