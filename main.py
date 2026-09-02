from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()

# In-memory database & ID counter
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Build a CRUD API", "done": False},
]
id_counter = 4

# Pydantic schemas for input validation
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# Stage 1 Endpoints
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Stage 2 Endpoints
@app.get("/tasks")
def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")

# Stage 3 Endpoint
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    global id_counter
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or blank"
        )

    new_task = {
        "id": id_counter,
        "title": payload.title.strip(),
        "done": False
    }
    tasks_db.append(new_task)
    id_counter += 1
    return new_task

# Stage 4: Update a task (PUT)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    # Find the task
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")

    # Ensure at least one field is provided for update
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (title or done) must be provided"
        )

    # Validate and update title if provided
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty or blank"
            )
        task["title"] = payload.title.strip()

    # Update done status if provided
    if payload.done is not None:
        task["done"] = payload.done

    return task

# Stage 4: Delete a task (DELETE)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    global tasks_db
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")

    # Remove task from list
    tasks_db = [t for t in tasks_db if t["id"] != task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)