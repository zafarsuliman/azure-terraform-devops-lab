from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database = tmp_path / "test.db"
    monkeypatch.setattr("app.config.settings", type("Settings", (), {"database_path": str(database), "environment": "test"})())
    monkeypatch.setattr("app.database.settings", type("Settings", (), {"database_path": str(database)})())
    monkeypatch.setattr("app.main.settings", type("Settings", (), {"environment": "test"})())
    from app.database import initialise
    initialise()
    yield
