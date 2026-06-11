import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.shared.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role = Column(String(20), default="parent")  # parent / child
    nickname = Column(String(50), default="")
    avatar = Column(String(200), default="")


class LoginSession(Base):
    """扫码登录会话"""

    __tablename__ = "login_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=True)
    status = Column(String(20), default="pending")  # pending / scanned / confirmed
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
