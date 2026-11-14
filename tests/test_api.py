from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_readiness():
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").status_code == 200


def test_crud_lifecycle():
    created = client.post("/tasks", json={"title": "Ship release", "description": "Run checks"})
    assert created.status_code == 201
    task_id = created.json()["id"]
    assert client.get(f"/tasks/{task_id}").json()["title"] == "Ship release"
    updated = client.patch(f"/tasks/{task_id}", json={"status": "done"})
    assert updated.json()["status"] == "done"
    assert len(client.get("/tasks", params={"status_filter": "done"}).json()) == 1
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_validation_and_missing_resource():
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.get("/tasks/999").status_code == 404
    assert client.get("/tasks", params={"limit": 101}).status_code == 422
