import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI(
    title="Task API (SQLite)",
    version="2.0",
    description="A CRUD API backed by a SQLite database.",
)

DB_NAME = "tasks.db"


# --- Database Helper Functions ---
def get_db_connection():
    """Establishes a connection to SQLite with dictionary-like row formatting."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes table schema and inserts initial seed tasks on first run."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tasks table if it does not exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """
    )
    conn.commit()

    # Check if table is empty; insert initial seed data if empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_tasks = [
            ("Buy grocery", False),
            ("Read a book", True),
            ("Build a CRUD API with SQL", False),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", seed_tasks
        )
        conn.commit()

    conn.close()


# Run DB initialization when app starts
init_db()


# --- Input Models ---
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# --- Stage 1: Root & Health Endpoints ---
@app.get("/")
def read_root():
    return {"name": "Task API (SQLite)", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Stage 1: Database Read Endpoints ---
@app.get("/tasks")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    if search is not None:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
        )

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


# --- Stage 2: Database Insert Endpoint ---
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or blank",
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (payload.title.strip(), False),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": payload.title.strip(), "done": False}


# --- Stage 3: Database Update & Delete Endpoints ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (title or done) must be provided",
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if task exists
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
        )

    current_title = row["title"]
    current_done = row["done"]

    # Validate new title if provided
    if payload.title is not None:
        if not payload.title.strip():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty or blank",
            )
        current_title = payload.title.strip()

    if payload.done is not None:
        current_done = payload.done

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (current_title, current_done, task_id),
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": current_title, "done": bool(current_done)}


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
        )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Optional Extras: Stats Endpoint ---
@app.get("/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    completed = cursor.fetchone()[0]

    conn.close()
    return {"total": total, "done": completed, "open": total - completed}