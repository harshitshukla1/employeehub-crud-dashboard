from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, create_engine, func, or_
from sqlalchemy.orm import Session, declarative_base, sessionmaker


# ============================================================
# Database Configuration
# ============================================================

DATABASE_URL = "sqlite:///./employeehub_step3.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    Provide a database session for each request.

    The session is created when a request starts and closed when
    the request finishes.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# SQLAlchemy Database Model
# ============================================================

class EmployeeModel(Base):
    """
    SQLAlchemy model mapped to the employees database table.
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    employee_code = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

    department = Column(String(50), nullable=False)
    designation = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=True)


# ============================================================
# Pydantic Schemas
# ============================================================

class EmployeeCreate(BaseModel):
    """
    Request schema used to create a new employee.
    """

    employee_code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        examples=["EMP003"],
        description="Unique employee code"
    )

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["Rohit"],
        description="Employee first name"
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["Verma"],
        description="Employee last name"
    )

    email: str = Field(
        ...,
        examples=["rohit.verma@company.com"],
        description="Employee email address"
    )

    department: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["data"],
        description="Employee department"
    )

    designation: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Data Engineer"],
        description="Employee job title"
    )

    salary: float = Field(
        ...,
        ge=0,
        examples=[90000],
        description="Employee salary. It cannot be negative."
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        """
        Validate basic email format.
        """

        value = value.strip().lower()

        if "@" not in value:
            raise ValueError("Email must contain '@'")

        if "." not in value.split("@")[-1]:
            raise ValueError("Email domain is not valid")

        return value

    @field_validator("department")
    @classmethod
    def normalize_department(cls, value):
        """
        Normalize department value to lowercase.
        """

        return value.strip().lower()


class EmployeeUpdate(BaseModel):
    """
    Request schema used to update an existing employee.

    All fields are optional because update operations may update
    only one or a few fields.
    """

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = None
    department: Optional[str] = Field(None, min_length=2, max_length=50)
    designation: Optional[str] = Field(None, min_length=2, max_length=100)
    salary: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        """
        Validate basic email format if email is provided.
        """

        if value is None:
            return value

        value = value.strip().lower()

        if "@" not in value:
            raise ValueError("Email must contain '@'")

        if "." not in value.split("@")[-1]:
            raise ValueError("Email domain is not valid")

        return value

    @field_validator("department")
    @classmethod
    def normalize_department(cls, value):
        """
        Normalize department value to lowercase if provided.
        """

        if value is None:
            return value

        return value.strip().lower()


class EmployeeResponse(BaseModel):
    """
    Response schema returned by employee API endpoints.
    """

    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    department: str
    designation: str
    salary: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class EmployeeListResponse(BaseModel):
    """
    Response schema for employee list endpoint.
    """

    total: int
    employees: List[EmployeeResponse]


# ============================================================
# Database Initialization
# ============================================================

def seed_initial_data():
    """
    Insert sample employees only if the table is empty.
    """

    db = SessionLocal()

    try:
        existing_count = db.query(EmployeeModel).count()

        if existing_count > 0:
            return

        sample_employees = [
            EmployeeModel(
                employee_code="EMP001",
                first_name="Aarav",
                last_name="Sharma",
                email="aarav.sharma@company.com",
                department="engineering",
                designation="Backend Developer",
                salary=85000,
                is_active=True,
            ),
            EmployeeModel(
                employee_code="EMP002",
                first_name="Priya",
                last_name="Singh",
                email="priya.singh@company.com",
                department="data",
                designation="Data Engineer",
                salary=95000,
                is_active=True,
            ),
        ]

        db.add_all(sample_employees)
        db.commit()

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create database tables and insert initial data when the app starts.
    """

    Base.metadata.create_all(bind=engine)
    seed_initial_data()

    yield


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="EmployeeHub Step 3 - SQLite CRUD API",
    version="3.0.0",
    description="""
    Step 3 project:
    - REST API
    - SQLite database
    - SQLAlchemy ORM
    - Persistent CRUD operations
    - Interactive dashboard
    """,
    lifespan=lifespan
)


# ============================================================
# Helper Functions
# ============================================================

def get_employee_or_404(db: Session, employee_id: int):
    """
    Return an employee by ID or raise a 404 error if not found.
    """

    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )

    return employee


def employee_code_exists(db: Session, employee_code: str):
    """
    Check whether an employee code already exists.
    """

    return (
        db.query(EmployeeModel)
        .filter(func.lower(EmployeeModel.employee_code) == employee_code.lower())
        .first()
        is not None
    )


def email_exists(db: Session, email: str, ignore_employee_id: Optional[int] = None):
    """
    Check whether an email address already exists.
    """

    query = db.query(EmployeeModel).filter(func.lower(EmployeeModel.email) == email.lower())

    if ignore_employee_id is not None:
        query = query.filter(EmployeeModel.id != ignore_employee_id)

    return query.first() is not None


# ============================================================
# UI Endpoints
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmployeeHub Step 3</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #0f172a, #312e81);
                color: white;
                min-height: 100vh;
            }

            .hero {
                padding: 70px 24px;
                text-align: center;
            }

            .card {
                background: rgba(255, 255, 255, 0.12);
                padding: 40px;
                border-radius: 24px;
                box-shadow: 0 25px 60px rgba(0,0,0,0.35);
                backdrop-filter: blur(10px);
                max-width: 1000px;
                margin: auto;
            }

            h1 {
                font-size: 48px;
                margin-bottom: 10px;
            }

            p {
                font-size: 18px;
                line-height: 1.6;
                color: #e5e7eb;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 30px;
            }

            .feature {
                padding: 20px;
                border-radius: 16px;
                background: rgba(255,255,255,0.12);
                text-align: left;
                border: 1px solid rgba(255,255,255,0.12);
            }

            .feature strong {
                display: block;
                font-size: 20px;
                margin-bottom: 8px;
            }

            a {
                display: inline-block;
                margin: 10px;
                padding: 14px 22px;
                border-radius: 12px;
                text-decoration: none;
                background: white;
                color: #312e81;
                font-weight: bold;
                transition: 0.25s;
            }

            a:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(0,0,0,0.3);
            }

            .badge {
                display: inline-block;
                margin-top: 20px;
                padding: 8px 16px;
                border-radius: 50px;
                background: rgba(34,197,94,0.25);
                border: 1px solid rgba(34,197,94,0.5);
            }

            @media (max-width: 800px) {
                .grid {
                    grid-template-columns: 1fr;
                }

                h1 {
                    font-size: 34px;
                }
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="card">
                <h1>EmployeeHub SQLite CRUD 🚀</h1>
                <p>
                    Step 3 adds a persistent SQLite database using SQLAlchemy ORM.
                    Employees created from the dashboard will remain available even after server restart.
                </p>

                <div class="grid">
                    <div class="feature">
                        <strong>SQLite Database</strong>
                        Data is stored in a real database file.
                    </div>
                    <div class="feature">
                        <strong>SQLAlchemy ORM</strong>
                        Python classes are mapped to database tables.
                    </div>
                    <div class="feature">
                        <strong>Persistent CRUD</strong>
                        Create, read, update, and delete records permanently.
                    </div>
                </div>

                <div style="margin-top: 32px;">
                    <a href="/dashboard">Open Dashboard</a>
                    <a href="/docs">Open Swagger Docs</a>
                    <a href="/api/v1/employees">View Employees JSON</a>
                    <a href="/api/v1/employees/stats/summary">View Stats</a>
                </div>

                <div class="badge">
                    SQLite-backed API Running ✅
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmployeeHub Database Dashboard</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #020617;
                color: #e5e7eb;
            }

            header {
                padding: 28px;
                background: linear-gradient(135deg, #2563eb, #7c3aed);
                color: white;
                text-align: center;
            }

            header h1 {
                margin: 0;
                font-size: 36px;
            }

            header p {
                margin: 10px 0 0;
                color: #e0e7ff;
            }

            .container {
                max-width: 1200px;
                margin: 24px auto;
                padding: 0 18px;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 24px;
            }

            .stat-card {
                background: #0f172a;
                padding: 20px;
                border-radius: 16px;
                border: 1px solid #1e293b;
            }

            .stat-card h3 {
                margin: 0;
                color: #94a3b8;
                font-size: 14px;
            }

            .stat-card p {
                margin: 10px 0 0;
                font-size: 28px;
                font-weight: bold;
            }

            .layout {
                display: grid;
                grid-template-columns: 380px 1fr;
                gap: 20px;
            }

            .panel {
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 18px;
                padding: 20px;
            }

            .panel h2 {
                margin-top: 0;
            }

            input, select {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                border-radius: 10px;
                border: 1px solid #334155;
                background: #020617;
                color: #e5e7eb;
            }

            button {
                border: none;
                padding: 12px 16px;
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
                margin: 5px 4px 5px 0;
            }

            .btn-primary {
                background: #2563eb;
                color: white;
            }

            .btn-danger {
                background: #dc2626;
                color: white;
            }

            .btn-warning {
                background: #f59e0b;
                color: #111827;
            }

            .btn-secondary {
                background: #334155;
                color: white;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                overflow: hidden;
                border-radius: 14px;
            }

            th, td {
                padding: 12px;
                border-bottom: 1px solid #1e293b;
                text-align: left;
                font-size: 14px;
            }

            th {
                background: #1e293b;
                color: #cbd5e1;
            }

            tr:hover {
                background: #111827;
            }

            .status-active {
                color: #22c55e;
                font-weight: bold;
            }

            .status-inactive {
                color: #ef4444;
                font-weight: bold;
            }

            .message {
                margin: 12px 0;
                padding: 12px;
                border-radius: 10px;
                display: none;
            }

            .success {
                background: rgba(34,197,94,0.15);
                border: 1px solid rgba(34,197,94,0.4);
                color: #86efac;
            }

            .error {
                background: rgba(239,68,68,0.15);
                border: 1px solid rgba(239,68,68,0.4);
                color: #fca5a5;
            }

            .search-row {
                display: grid;
                grid-template-columns: 1fr 1fr auto;
                gap: 10px;
                margin-bottom: 16px;
            }

            .hint {
                margin-top: 10px;
                font-size: 13px;
                color: #94a3b8;
            }

            @media (max-width: 1000px) {
                .layout {
                    grid-template-columns: 1fr;
                }

                .stats {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 600px) {
                .stats {
                    grid-template-columns: 1fr;
                }

                .search-row {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>

    <body>
        <header>
            <h1>EmployeeHub Database Dashboard 🚀</h1>
            <p>This dashboard uses FastAPI + SQLite + SQLAlchemy</p>
        </header>

        <div class="container">

            <div class="stats">
                <div class="stat-card">
                    <h3>Total Employees</h3>
                    <p id="totalEmployees">0</p>
                </div>
                <div class="stat-card">
                    <h3>Active</h3>
                    <p id="activeEmployees">0</p>
                </div>
                <div class="stat-card">
                    <h3>Inactive</h3>
                    <p id="inactiveEmployees">0</p>
                </div>
                <div class="stat-card">
                    <h3>Avg Salary</h3>
                    <p id="avgSalary">0</p>
                </div>
            </div>

            <div class="layout">
                <div class="panel">
                    <h2 id="formTitle">Add Employee</h2>

                    <div id="message" class="message"></div>

                    <input type="hidden" id="employeeId">

                    <label>Employee Code</label>
                    <input id="employeeCode" placeholder="EMP003">

                    <label>First Name</label>
                    <input id="firstName" placeholder="Rohit">

                    <label>Last Name</label>
                    <input id="lastName" placeholder="Verma">

                    <label>Email</label>
                    <input id="email" placeholder="rohit.verma@company.com">

                    <label>Department</label>
                    <select id="department">
                        <option value="data">Data</option>
                        <option value="engineering">Engineering</option>
                        <option value="product">Product</option>
                        <option value="hr">HR</option>
                        <option value="finance">Finance</option>
                    </select>

                    <label>Designation</label>
                    <input id="designation" placeholder="Data Engineer">

                    <label>Salary</label>
                    <input id="salary" type="number" placeholder="90000">

                    <button class="btn-primary" onclick="submitEmployee()">Save Employee</button>
                    <button class="btn-secondary" onclick="resetForm()">Reset</button>

                    <div class="hint">
                        Tip: Add an employee, restart the server, and verify that the employee still exists.
                    </div>
                </div>

                <div class="panel">
                    <h2>Employees</h2>

                    <div class="search-row">
                        <input id="searchInput" placeholder="Search by name, email, or code">
                        <select id="filterDepartment">
                            <option value="">All Departments</option>
                            <option value="data">Data</option>
                            <option value="engineering">Engineering</option>
                            <option value="product">Product</option>
                            <option value="hr">HR</option>
                            <option value="finance">Finance</option>
                        </select>
                        <button class="btn-primary" onclick="loadEmployees()">Search</button>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Code</th>
                                <th>Name</th>
                                <th>Department</th>
                                <th>Salary</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="employeesTable">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            async function loadStats() {
                const response = await fetch('/api/v1/employees/stats/summary');
                const data = await response.json();

                document.getElementById('totalEmployees').innerText = data.total_employees;
                document.getElementById('activeEmployees').innerText = data.active_employees;
                document.getElementById('inactiveEmployees').innerText = data.inactive_employees;
                document.getElementById('avgSalary').innerText = '₹' + data.average_salary;
            }

            async function loadEmployees() {
                const search = document.getElementById('searchInput').value;
                const department = document.getElementById('filterDepartment').value;

                const params = new URLSearchParams();

                if (search) {
                    params.append('search', search);
                }

                if (department) {
                    params.append('department', department);
                }

                const url = '/api/v1/employees?' + params.toString();

                const response = await fetch(url);
                const data = await response.json();

                const table = document.getElementById('employeesTable');
                table.innerHTML = '';

                data.employees.forEach(employee => {
                    const row = document.createElement('tr');

                    row.innerHTML = `
                        <td>${employee.id}</td>
                        <td>${employee.employee_code}</td>
                        <td>${employee.first_name} ${employee.last_name}</td>
                        <td>${employee.department}</td>
                        <td>₹${employee.salary}</td>
                        <td class="${employee.is_active ? 'status-active' : 'status-inactive'}">
                            ${employee.is_active ? 'Active' : 'Inactive'}
                        </td>
                        <td>
                            <button class="btn-warning" onclick="editEmployee(${employee.id})">Edit</button>
                            <button class="btn-danger" onclick="deleteEmployee(${employee.id})">Delete</button>
                        </td>
                    `;

                    table.appendChild(row);
                });

                await loadStats();
            }

            async function submitEmployee() {
                const employeeId = document.getElementById('employeeId').value;

                const payload = {
                    first_name: document.getElementById('firstName').value,
                    last_name: document.getElementById('lastName').value,
                    email: document.getElementById('email').value,
                    department: document.getElementById('department').value,
                    designation: document.getElementById('designation').value,
                    salary: Number(document.getElementById('salary').value)
                };

                let url = '/api/v1/employees';
                let method = 'POST';

                if (!employeeId) {
                    payload.employee_code = document.getElementById('employeeCode').value;
                } else {
                    url = `/api/v1/employees/${employeeId}`;
                    method = 'PUT';
                }

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (!response.ok) {
                    showMessage(JSON.stringify(data.detail), 'error');
                    return;
                }

                showMessage(employeeId ? 'Employee updated successfully' : 'Employee created successfully', 'success');
                resetForm();
                await loadEmployees();
            }

            async function editEmployee(id) {
                const response = await fetch(`/api/v1/employees/${id}`);
                const employee = await response.json();

                document.getElementById('formTitle').innerText = 'Update Employee';
                document.getElementById('employeeId').value = employee.id;
                document.getElementById('employeeCode').value = employee.employee_code;
                document.getElementById('employeeCode').disabled = true;
                document.getElementById('firstName').value = employee.first_name;
                document.getElementById('lastName').value = employee.last_name;
                document.getElementById('email').value = employee.email;
                document.getElementById('department').value = employee.department;
                document.getElementById('designation').value = employee.designation;
                document.getElementById('salary').value = employee.salary;

                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            async function deleteEmployee(id) {
                const confirmDelete = confirm('Are you sure you want to delete this employee?');

                if (!confirmDelete) {
                    return;
                }

                const response = await fetch(`/api/v1/employees/${id}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (!response.ok) {
                    showMessage(JSON.stringify(data.detail), 'error');
                    return;
                }

                showMessage('Employee deleted successfully', 'success');
                await loadEmployees();
            }

            function resetForm() {
                document.getElementById('formTitle').innerText = 'Add Employee';
                document.getElementById('employeeId').value = '';
                document.getElementById('employeeCode').value = '';
                document.getElementById('employeeCode').disabled = false;
                document.getElementById('firstName').value = '';
                document.getElementById('lastName').value = '';
                document.getElementById('email').value = '';
                document.getElementById('department').value = 'data';
                document.getElementById('designation').value = '';
                document.getElementById('salary').value = '';
            }

            function showMessage(text, type) {
                const message = document.getElementById('message');
                message.innerText = text;
                message.className = 'message ' + type;
                message.style.display = 'block';

                setTimeout(() => {
                    message.style.display = 'none';
                }, 4000);
            }

            loadEmployees();
        </script>
    </body>
    </html>
    """


# ============================================================
# Basic Endpoints
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "EmployeeHub Step 3 API is running successfully",
        "database": "SQLite",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/info")
def api_info():
    return {
        "project": "EmployeeHub CRUD Dashboard",
        "step": "Step 3",
        "version": "3.0.0",
        "storage": "SQLite database",
        "orm": "SQLAlchemy",
        "features": [
            "FastAPI",
            "REST API",
            "SQLite",
            "SQLAlchemy ORM",
            "Persistent CRUD",
            "Interactive Dashboard"
        ]
    }


# ============================================================
# CRUD Endpoints
# ============================================================

@app.get("/api/v1/employees", response_model=EmployeeListResponse)
def get_employees(
    search: Optional[str] = Query(None, description="Search by name, email, or employee code"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
):
    """
    Return the list of employees.

    Optional query parameters:
    - search
    - department
    """

    query = db.query(EmployeeModel)

    if search:
        search_pattern = f"%{search.lower()}%"

        query = query.filter(
            or_(
                func.lower(EmployeeModel.first_name).like(search_pattern),
                func.lower(EmployeeModel.last_name).like(search_pattern),
                func.lower(EmployeeModel.email).like(search_pattern),
                func.lower(EmployeeModel.employee_code).like(search_pattern),
            )
        )

    if department:
        query = query.filter(func.lower(EmployeeModel.department) == department.lower())

    total = query.count()
    employees = query.order_by(EmployeeModel.id.asc()).all()

    return {
        "total": total,
        "employees": employees
    }


@app.get("/api/v1/employees/stats/summary")
def get_employee_stats(db: Session = Depends(get_db)):
    """
    Return employee summary statistics.
    """

    total_employees = db.query(func.count(EmployeeModel.id)).scalar() or 0

    active_employees = (
        db.query(func.count(EmployeeModel.id))
        .filter(EmployeeModel.is_active.is_(True))
        .scalar()
        or 0
    )

    average_salary = db.query(func.avg(EmployeeModel.salary)).scalar() or 0

    department_rows = (
        db.query(EmployeeModel.department, func.count(EmployeeModel.id))
        .group_by(EmployeeModel.department)
        .all()
    )

    department_counts = {
        department: count
        for department, count in department_rows
    }

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": total_employees - active_employees,
        "average_salary": round(float(average_salary), 2),
        "department_counts": department_counts
    }


@app.post(
    "/api/v1/employees",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeResponse
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new employee.
    """

    if employee_code_exists(db, employee_data.employee_code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee code '{employee_data.employee_code}' already exists"
        )

    if email_exists(db, employee_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{employee_data.email}' already exists"
        )

    new_employee = EmployeeModel(**employee_data.model_dump())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@app.get(
    "/api/v1/employees/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """
    Return a single employee by ID.
    """

    return get_employee_or_404(db, employee_id)


@app.put(
    "/api/v1/employees/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing employee.

    Only the fields provided in the request body will be updated.
    """

    employee = get_employee_or_404(db, employee_id)

    update_data = employee_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )

    if "email" in update_data:
        if email_exists(db, update_data["email"], ignore_employee_id=employee_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{update_data['email']}' already exists"
            )

    for field_name, field_value in update_data.items():
        setattr(employee, field_name, field_value)

    employee.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(employee)

    return employee


@app.delete("/api/v1/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete an employee by ID.
    """

    employee = get_employee_or_404(db, employee_id)

    db.delete(employee)
    db.commit()

    return {
        "message": "Employee deleted successfully",
        "deleted_employee_id": employee_id
    }