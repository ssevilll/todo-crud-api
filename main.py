from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Stage 2: In-memory database & ID counter
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Build a CRUD API", "done": False},
]
id_counter = 4

# Pydantic schema for task creation input validation
class TaskCreate(BaseModel):
    title: str

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
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# Stage 3: Create a new task with input validation
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    global id_counter
    
    # Input validation: check for blank/whitespace-only titles
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