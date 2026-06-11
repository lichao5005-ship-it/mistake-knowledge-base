import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.shared.config import settings
from app.modules.upload.models import SourceFile, UploadSession


def create_session(db: Session, user_id: int, subject_id: int) -> UploadSession:
    session = UploadSession(user_id=user_id, subject_id=subject_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


async def save_upload_file(
    db: Session, session_id: int, file: UploadFile
) -> SourceFile:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = upload_dir / unique_name

    content = await file.read()
    file_path.write_bytes(content)

    sf = SourceFile(
        session_id=session_id,
        file_name=file.filename or unique_name,
        file_path=str(file_path),
        file_type=ext,
    )
    db.add(sf)
    db.commit()
    db.refresh(sf)
    return sf
