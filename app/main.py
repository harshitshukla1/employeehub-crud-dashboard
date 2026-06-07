"""
Production entrypoint for EmployeeHub CRUD Dashboard.

This file exposes the latest stable FastAPI application.
Learning versions are kept separately as step files.
"""

from app.step_03_sqlite_crud import app


app.title = "EmployeeHub CRUD Dashboard"
app.version = "1.0.0"
app.description = """
EmployeeHub is a production-style CRUD dashboard built with FastAPI.

Features:
- REST API
- SQLite database
- SQLAlchemy ORM
- Pydantic validation
- Interactive dashboard UI
- Automated tests
- GitHub Actions CI pipeline
"""
