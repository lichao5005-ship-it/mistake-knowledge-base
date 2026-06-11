import pytest


@pytest.mark.asyncio
async def test_list_subjects(client, seed_subjects):
    resp = await client.get("/api/knowledge/subjects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["name"] == "语文"


@pytest.mark.asyncio
async def test_subject_response_shape(client, seed_subjects):
    resp = await client.get("/api/knowledge/subjects")
    item = resp.json()[0]
    assert "id" in item
    assert "name" in item
    assert "icon" in item
