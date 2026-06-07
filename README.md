# EmployeeHub CRUD Dashboard

[![CI - FastAPI CRUD API](https://github.com/harshitshukla1/employeehub-crud-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/harshitshukla1/employeehub-crud-dashboard/actions/workflows/ci.yml)

EmployeeHub is a production-style CRUD dashboard built with **FastAPI**, **SQLite**, **SQLAlchemy**, **Pydantic**, **Pytest**, and **GitHub Actions CI**.

This project demonstrates how to build a REST API, connect it with an interactive browser dashboard, persist data in a database, write automated tests, and run those tests automatically on every GitHub push.

---

## Author

**Harshit Shukla**

---

## Project Overview

EmployeeHub is an employee management application where users can:

- Create employees
- View employee records
- Search employees
- Filter employees by department
- Update employee details
- Delete employees
- View dashboard statistics
- Test REST API endpoints using Swagger UI

The project is built step-by-step to clearly demonstrate the evolution from a basic FastAPI app to a database-backed CRUD dashboard.

---

## Key Features

- FastAPI REST API
- Interactive dashboard using HTML, CSS, and JavaScript
- Employee CRUD operations
- SQLite database persistence
- SQLAlchemy ORM
- Pydantic request validation
- Search and department filtering
- Dashboard summary statistics
- Automated API tests using Pytest
- GitHub Actions CI pipeline
- Separate learning versions for each project stage

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Backend REST API framework |
| Uvicorn | ASGI server to run FastAPI |
| SQLite | Lightweight file-based database |
| SQLAlchemy | ORM for database operations |
| Pydantic | Request and response validation |
| Pytest | Automated testing |
| HTTPX / TestClient | API testing support |
| GitHub Actions | Continuous Integration pipeline |
| HTML/CSS/JavaScript | Interactive browser dashboard |
| GitHub Codespaces | Cloud development environment |

---

## Project Structure

```text
employeehub-crud-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── step_01_basic_fastapi.py
│   ├── step_02_in_memory_crud.py
│   └── step_03_sqlite_crud.py
│
├── tests/
│   └── test_step_03_sqlite_crud.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Learning Versions

This repository keeps separate learning versions so the project journey is easy to understand.

| File | Description |
|---|---|
| `app/step_01_basic_fastapi.py` | Basic FastAPI application with landing page and health endpoint |
| `app/step_02_in_memory_crud.py` | In-memory CRUD API with mini interactive dashboard |
| `app/step_03_sqlite_crud.py` | SQLite + SQLAlchemy CRUD API with persistent dashboard |
| `app/main.py` | Final production-style entrypoint |

---

## How the Application Works

High-level flow:

```text
Browser Dashboard
        ↓
JavaScript fetch()
        ↓
FastAPI REST API
        ↓
SQLAlchemy ORM
        ↓
SQLite Database
```

When the dashboard loads, JavaScript calls the FastAPI backend using `fetch()`.

Example:

```javascript
fetch("/api/v1/employees")
```

FastAPI receives the request, queries the SQLite database using SQLAlchemy, and returns JSON data to the browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Landing page |
| GET | `/dashboard` | Interactive employee dashboard |
| GET | `/health` | API health check |
| GET | `/api/v1/info` | API information |
| GET | `/api/v1/employees` | List all employees |
| POST | `/api/v1/employees` | Create a new employee |
| GET | `/api/v1/employees/{employee_id}` | Get employee by ID |
| PUT | `/api/v1/employees/{employee_id}` | Update employee by ID |
| DELETE | `/api/v1/employees/{employee_id}` | Delete employee by ID |
| GET | `/api/v1/employees/stats/summary` | Employee summary statistics |

---

## Example Create Employee Request

Endpoint:

```text
POST /api/v1/employees
```

Request body:

```json
{
  "employee_code": "EMP003",
  "first_name": "Rohit",
  "last_name": "Verma",
  "email": "rohit.verma@company.com",
  "department": "data",
  "designation": "Data Engineer",
  "salary": 90000
}
```

Example response:

```json
{
  "id": 3,
  "employee_code": "EMP003",
  "first_name": "Rohit",
  "last_name": "Verma",
  "email": "rohit.verma@company.com",
  "department": "data",
  "designation": "Data Engineer",
  "salary": 90000,
  "is_active": true,
  "created_at": "2026-06-07T10:20:30",
  "updated_at": null
}
```

---

## Validation Examples

The API uses Pydantic validation.

Invalid salary:

```json
{
  "salary": -5000
}
```

This returns:

```text
422 Unprocessable Entity
```

Duplicate employee code or email returns:

```text
409 Conflict
```

Employee not found returns:

```text
404 Not Found
```

---

## Run This Project Using GitHub Codespaces

You do not need to install anything on your local computer.

### Step 1: Open the Repository

Open this GitHub repository:

```text
https://github.com/harshitshukla1/employeehub-crud-dashboard
```

### Step 2: Open GitHub Codespaces

Click:

```text
Code → Codespaces → Create codespace on main
```

Wait until the cloud VS Code environment opens.

### Step 3: Install Dependencies

In the Codespaces terminal, run:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Final Application

Run:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Open the Browser Preview

GitHub Codespaces will show a popup for port `8000`.

Click:

```text
Open in Browser
```

Now open:

```text
/
```

Dashboard:

```text
/dashboard
```

Swagger API documentation:

```text
/docs
```

---

## Run Specific Learning Versions

### Step 1: Basic FastAPI App

```bash
python -m uvicorn app.step_01_basic_fastapi:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: In-Memory CRUD App

```bash
python -m uvicorn app.step_02_in_memory_crud:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: SQLite + SQLAlchemy CRUD App

```bash
python -m uvicorn app.step_03_sqlite_crud:app --host 0.0.0.0 --port 8000 --reload
```

### Final App Entrypoint

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Run Tests

Run automated tests:

```bash
python -m pytest -q
```

Expected result:

```text
15 passed
```

Warnings may appear depending on package versions, but all tests should pass.

---

## Test Coverage Areas

The test suite verifies:

- Health endpoint
- Empty employee list
- Employee creation
- Duplicate employee code handling
- Duplicate email handling
- Get employee by ID
- Employee not found handling
- Employee update
- Empty update body validation
- Employee delete
- Search functionality
- Department filtering
- Negative salary validation
- Invalid email validation
- Employee statistics endpoint

---

## Continuous Integration

This project uses **GitHub Actions** for Continuous Integration.

Workflow file:

```text
.github/workflows/ci.yml
```

On every push to the `main` branch, GitHub Actions automatically:

1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Runs Pytest test suite
5. Compiles Python files

If tests pass, the pipeline shows a green check.

If tests fail, the pipeline turns red and deployment should not proceed.

---

## Database Behavior

This project uses SQLite for learning and development.

The database file is created automatically when the app starts.

SQLite database files are ignored by Git using `.gitignore`:

```gitignore
*.db
*.sqlite
*.sqlite3
```

This is intentional because database files are runtime-generated and should not be committed to GitHub.

---

## Important Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run final app:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Run tests:

```bash
python -m pytest -q
```

Check Git status:

```bash
git status
```

Commit changes:

```bash
git add .
git commit -m "Your commit message"
git push
```

---

## What This Project Demonstrates

This project demonstrates practical understanding of:

- REST API design
- FastAPI routing
- HTTP methods: GET, POST, PUT, DELETE
- HTTP status codes
- Request body validation
- Path parameters
- Query parameters
- JSON responses
- HTML responses
- SQLite database persistence
- SQLAlchemy ORM models
- Database session handling
- CRUD operations
- Error handling using `HTTPException`
- Interactive frontend calling backend APIs
- Automated testing with Pytest
- CI pipeline with GitHub Actions
- GitHub Codespaces development workflow

---

## Future Improvements

Planned improvements:

- Add JWT authentication
- Add pagination
- Add Docker support
- Deploy to Render
- Replace SQLite with PostgreSQL for production
- Add role-based access control
- Add frontend static file separation
- Add logging middleware
- Add production-ready settings management

---

## Status

Current status:

```text
Project Stage: CRUD API + SQLite + Tests + CI
CI Status: Passing
Deployment: Upcoming
```

---

## Author

**Harshit Shukla**

GitHub:

```text
https://github.com/harshitshukla1
```