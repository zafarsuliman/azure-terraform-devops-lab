import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, Response, status

from .config import settings
from .database import connect, initialise, transaction
from .models import Task, TaskCreate, TaskUpdate


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname, "message": record.getMessage()})


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("task_api")
logger.handlers = [handler]
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise()
    yield


app = FastAPI(title="Azure Task API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    response: Response = await call_next(request)
    response.headers["x-request-id"] = request_id
    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )
    )
    return response


def _get(task_id: int) -> Task:
    with connect() as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**dict(row))


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/ready", tags=["operations"])
def ready() -> dict[str, str]:
    try:
        with connect() as connection:
            connection.execute("SELECT 1").fetchone()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    now = datetime.now(timezone.utc).isoformat()
    with transaction() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks(title, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (payload.title, payload.description, payload.status.value, now, now),
        )
        task_id = int(cursor.lastrowid)
    return _get(task_id)


@app.get("/tasks", response_model=list[Task])
def list_tasks(status_filter: str | None = None, limit: int = 50, offset: int = 0) -> list[Task]:
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="limit must be 1-100 and offset non-negative")
    query, params = "SELECT * FROM tasks", []
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
    query += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [Task(**dict(row)) for row in rows]


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    return _get(task_id)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    current = _get(task_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return current
    values = current.model_dump()
    values.update(changes)
    now = datetime.now(timezone.utc).isoformat()
    task_status = values["status"].value if hasattr(values["status"], "value") else values["status"]
    with transaction() as connection:
        connection.execute(
            "UPDATE tasks SET title=?, description=?, status=?, updated_at=? WHERE id=?",
            (values["title"], values["description"], task_status, now, task_id),
        )
    return _get(task_id)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    _get(task_id)
    with transaction() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
