# Task API (SQLite Database Edition)

A RESTful CRUD API built with Python and FastAPI for managing a to-do list, now backed by a persistent SQLite database.

## Database Documentation

### Why SQLite Was Chosen
- **Zero Configuration:** SQLite requires no separate server installation, daemon processes, or user authentication setup.
- **Portability:** The entire database resides in a single lightweight file (`tasks.db`), making it ideal for fast local development and lightweight applications.
- **Simplicity:** It provides full SQL capability and standard transaction support without infrastructure overhead.

### Database Location & Auto-Initialization
- **File Location:** `./tasks.db` (root directory of the project)
- **Automatic Setup:** When the server starts up, it automatically creates the `tasks` table if it does not exist and populates three default example tasks if the database is empty.

---

## How to Start the Project

1. **Clone the repository:**
   ```bash
   git clone <YOUR-GITHUB-REPO-URL>
   cd task-api
