# Task API (To-Do List CRUD API)

A lightweight RESTful API built with Python and FastAPI for managing a to-do list in memory.

## How to Install and Run

```bash
# 1. Clone the repository
git clone <YOUR-GITHUB-REPO-URL>
cd task-api

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install fastapi uvicorn

# 4. Start the server
uvicorn main:app --reload --port 8000
