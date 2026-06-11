import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.modules.auth.models import LoginSession, User


def get_or_create_default_user(db: Session) -> User:
    """第一版：自动创建默认用户"""
    user = db.query(User).first()
    if not user:
        user = User(role="parent", nickname="家长")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_qr_session(db: Session) -> LoginSession:
    session = LoginSession(
        session_id=str(uuid.uuid4()),
        status="pending",
        expires_at=datetime.now() + timedelta(minutes=5),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def verify_session(db: Session, session_id: str) -> User | None:
    ls = db.query(LoginSession).filter(
        LoginSession.session_id == session_id,
        LoginSession.status == "pending",
        LoginSession.expires_at > datetime.now(),
    ).first()
    if not ls:
        return None
    user = get_or_create_default_user(db)
    ls.user_id = user.id
    ls.status = "confirmed"
    db.commit()
    return user
