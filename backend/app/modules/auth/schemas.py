from pydantic import BaseModel


class QrCreateResponse(BaseModel):
    session_id: str
    qr_image: str
    login_url: str
    expires_at: str


class QrVerifyResponse(BaseModel):
    user_id: int
    role: str
    nickname: str


class QrStatusResponse(BaseModel):
    status: str
