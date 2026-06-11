import pytest


@pytest.mark.asyncio
async def test_create_qr(client):
    resp = await client.post("/api/auth/qr/create?base_url=http://localhost:8000")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "qr_image" in data
    assert data["qr_image"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_verify_nonexistent_session(client):
    resp = await client.post("/api/auth/qr/verify/nonexistent")
    assert resp.status_code == 418


@pytest.mark.asyncio
async def test_full_qr_flow(client):
    # 创建二维码
    resp = await client.post("/api/auth/qr/create")
    session_id = resp.json()["session_id"]

    # 验证状态是 pending
    status_resp = await client.get(f"/api/auth/qr/status/{session_id}")
    assert status_resp.json()["status"] == "pending"

    # 手机扫码验证
    verify_resp = await client.post(f"/api/auth/qr/verify/{session_id}")
    assert verify_resp.status_code == 200

    # 状态变为 confirmed
    status_resp2 = await client.get(f"/api/auth/qr/status/{session_id}")
    assert status_resp2.json()["status"] == "confirmed"
