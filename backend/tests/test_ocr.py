import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.modules.upload.models import SourceFile

FAKE_OCR_RESPONSE = """{
  "questions": [
    {
      "number": "1",
      "content": "32 × 15 = ?",
      "student_answer": "480",
      "blank_exists": false
    },
    {
      "number": "2",
      "content": "25 + 37 = ?",
      "student_answer": "",
      "blank_exists": true
    }
  ],
  "subject_type": "数学"
}"""

FAKE_CORRECTION_RESPONSE = """{
  "is_correct": true,
  "correct_answer": "480",
  "error_type": "正确",
  "analysis": "32 × 15 可以拆成 32 × 10 + 32 × 5 = 320 + 160 = 480。你做对了！",
  "knowledge_point": "两位数乘法"
}"""


@pytest.fixture
def seed_source_file(db_session):
    """创建测试用的 SourceFile 记录 + 真实临时文件"""
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.write(b"fake-image-bytes")
    tmp.close()

    sf = SourceFile(
        file_name="test_homework.jpg",
        file_path=tmp.name,
        file_type="jpg",
        page_count=1,
    )
    db_session.add(sf)
    db_session.commit()
    yield sf
    Path(tmp.name).unlink(missing_ok=True)


@patch("app.modules.ocr.service.call_qwen_vision", return_value=FAKE_OCR_RESPONSE)
@patch(
    "app.modules.ocr.service.call_qwen_text",
    return_value=FAKE_CORRECTION_RESPONSE,
)
@pytest.mark.asyncio
async def test_process_file_success(
    mock_text, mock_vision, client, seed_source_file
):
    """测试成功处理一张图片：OCR → 判错 → 返回结果"""
    resp = await client.post(f"/api/ocr/process/{seed_source_file.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "ocr_result_id" in data
    assert data["status"] == "done"

    # 验证保存的判错结果
    result_resp = await client.get(f"/api/ocr/results/{data['ocr_result_id']}")
    assert result_resp.status_code == 200
    r = result_resp.json()
    assert len(r["corrections"]) == 2

    # 第1题：作答且正确
    c1 = r["corrections"][0]
    assert c1["question_number"] == "1"
    assert c1["student_answer"] == "480"
    assert c1["is_correct"] is True
    assert c1["error_type"] == "正确"

    # 第2题：未作答
    c2 = r["corrections"][1]
    assert c2["question_number"] == "2"
    assert c2["student_answer"] == ""
    assert c2["is_correct"] is False
    assert c2["error_type"] == "未作答"


@pytest.mark.asyncio
async def test_process_nonexistent_file(client):
    """测试处理不存在的文件时返回 404"""
    resp = await client.post("/api/ocr/process/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_result(client):
    """测试查询不存在的 OCR 结果时返回 404"""
    resp = await client.get("/api/ocr/results/9999")
    assert resp.status_code == 404
