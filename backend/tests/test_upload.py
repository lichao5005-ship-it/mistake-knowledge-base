import io
import os

import pytest


@pytest.mark.asyncio
async def test_create_session(client, db_session, seed_subjects):
    """创建上传会话"""
    resp = await client.post("/api/upload/session", data={"subject_id": 1, "user_id": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["subject_id"] == 1


@pytest.mark.asyncio
async def test_upload_files(client, db_session, seed_subjects):
    """上传文件到会话"""
    # 先创建会话
    session_resp = await client.post(
        "/api/upload/session", data={"subject_id": 1, "user_id": 1}
    )
    session_id = session_resp.json()["session_id"]

    # 上传文件
    file_content = b"fake-image-data"
    files = [
        ("files", ("test.jpg", io.BytesIO(file_content), "image/jpeg")),
    ]
    resp = await client.post(
        "/api/upload/files",
        data={"session_id": session_id},
        files=files,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == session_id
    assert len(data["files"]) == 1
    assert data["files"][0]["file_name"] == "test.jpg"


@pytest.mark.asyncio
async def test_upload_multiple_files(client, db_session, seed_subjects):
    """批量上传多个文件"""
    session_resp = await client.post(
        "/api/upload/session", data={"subject_id": 2, "user_id": 1}
    )
    session_id = session_resp.json()["session_id"]

    files = [
        ("files", ("page1.jpg", io.BytesIO(b"data1"), "image/jpeg")),
        ("files", ("page2.png", io.BytesIO(b"data2"), "image/png")),
    ]
    resp = await client.post(
        "/api/upload/files",
        data={"session_id": session_id},
        files=files,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["files"]) == 2
    assert data["files"][0]["file_name"] == "page1.jpg"
    assert data["files"][1]["file_name"] == "page2.png"
