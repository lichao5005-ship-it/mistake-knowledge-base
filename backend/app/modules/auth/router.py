import base64
import io

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.modules.auth import service as auth_service
from app.shared.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/qr/create")
def create_qr(
    base_url: str = Query("http://localhost:8000"),
    db: Session = Depends(get_db),
):
    """PC 端：生成登录二维码"""
    session = auth_service.create_qr_session(db)
    login_url = f"{base_url}/scan?session_id={session.session_id}"

    qr = qrcode.make(login_url)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "session_id": session.session_id,
        "qr_image": f"data:image/png;base64,{img_b64}",
        "login_url": login_url,
        "expires_at": session.expires_at.isoformat(),
    }


@router.post("/qr/verify/{session_id}")
def verify_qr(session_id: str, db: Session = Depends(get_db)):
    """手机端：扫码后验证"""
    user = auth_service.verify_session(db, session_id)
    if not user:
        raise HTTPException(418, "会话已过期或无效")
    return {"user_id": user.id, "role": user.role, "nickname": user.nickname}


@router.get("/qr/status/{session_id}")
def qr_status(session_id: str, db: Session = Depends(get_db)):
    """PC 端：轮询查询二维码状态"""
    from app.modules.auth.models import LoginSession

    ls = db.query(LoginSession).filter(
        LoginSession.session_id == session_id
    ).first()
    if not ls:
        raise HTTPException(404, "会话不存在")
    return {"status": ls.status}
