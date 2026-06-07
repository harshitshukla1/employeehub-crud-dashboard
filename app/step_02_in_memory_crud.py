from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="EmployeeHub Step 2 - In-Memory CRUD API",
    version="2.0.0",
    description="""
    Step 2 project:
    - REST API
    - In-memory CRUD
    - Pydantic validation
    - Mini interactive UI
    """
)


# ============================================================
# Pydantic Schemas
# ============================================================

class EmployeeCreate(BaseModel):
    """
    Request schema used to create a new employee.

    Used by:
    POST /api/v1/employees
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

    Used by:
    PUT /api/v1/employees/{employee_id}

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
    created_at: str
    updated_at: Optional[str] = None


# ============================================================
# In-Memory Database
# ============================================================

employees_db = [
    {
        "id": 1,
        "employee_code": "EMP001",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "email": "aarav.sharma@company.com",
        "department": "engineering",
        "designation": "Backend Developer",
        "salary": 85000,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
    },
    {
        "id": 2,
        "employee_code": "EMP002",
        "first_name": "Priya",
        "last_name": "Singh",
        "email": "priya.singh@company.com",
        "department": "data",
        "designation": "Data Engineer",
        "salary": 95000,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
    },
]

next_employee_id = 3


# ============================================================
# Helper Functions
# ============================================================

def find_employee_by_id(employee_id: int):
    """
    Find an employee by ID.

    Returns:
        dict: Employee data if found.
        None: If employee does not exist.
    """

    for employee in employees_db:
        if employee["id"] == employee_id:
            return employee

    return None


def check_duplicate_employee_code(employee_code: str):
    """
    Check whether an employee code already exists.
    """

    for employee in employees_db:
        if employee["employee_code"].lower() == employee_code.lower():
            return True

    return False


def check_duplicate_email(email: str, ignore_employee_id: Optional[int] = None):
    """
    Check whether an email address already exists.

    Args:
        email: Email address to check.
        ignore_employee_id: Employee ID to ignore during update operation.
    """

    for employee in employees_db:
        if ignore_employee_id is not None and employee["id"] == ignore_employee_id:
            continue

        if employee["email"].lower() == email.lower():
            return True

    return False


# ============================================================
# Home UI
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmployeeHub Step 2</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #141e30, #243b55);
                color: white;
                min-height: 100vh;
            }

            .hero {
                padding: 60px 24px;
                text-align: center;
            }

            .card {
                background: rgba(255, 255, 255, 0.12);
                padding: 35px;
                border-radius: 22px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.3);
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
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-top: 30px;
            }

            .method {
                padding: 18px;
                border-radius: 14px;
                background: rgba(255,255,255,0.12);
                text-align: left;
            }

            .method strong {
                display: block;
                font-size: 22px;
                margin-bottom: 8px;
            }

            .get { border-left: 6px solid #22c55e; }
            .post { border-left: 6px solid #3b82f6; }
            .put { border-left: 6px solid #f59e0b; }
            .delete { border-left: 6px solid #ef4444; }

            a {
                display: inline-block;
                margin: 10px;
                padding: 14px 22px;
                border-radius: 12px;
                text-decoration: none;
                background: white;
                color: #243b55;
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

            @media (max-width: 900px) {
                .grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 600px) {
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
                <h1>EmployeeHub CRUD 🚀</h1>
                <p>
                    Step 2 adds a FastAPI in-memory CRUD REST API.
                    You can now create, read, update, and delete employees.
                </p>

                <div class="grid">
                    <div class="method get">
                        <strong>GET</strong>
                        Read data
                    </div>
                    <div class="method post">
                        <strong>POST</strong>
                        Create new data
                    </div>
                    <div class="method put">
                        <strong>PUT</strong>
                        Update existing data
                    </div>
                    <div class="method delete">
                        <strong>DELETE</strong>
                        Delete data
                    </div>
                </div>

                <div style="margin-top: 32px;">
                    <a href="/dashboard">Open Mini Dashboard</a>
                    <a href="/docs">Open Swagger Docs</a>
                    <a href="/api/v1/employees">View Employees JSON</a>
                    <a href="/api/v1/employees/stats/summary">View Stats</a>
                </div>

                <div class="badge">
                    In-Memory CRUD API Running ✅
                </div>
            </div>
        </div>
    </body>
    </html>
    """


# ============================================================
# Mini Interactive Dashboard
# ============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmployeeHub Dashboard</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: #e5e7eb;
            }

            header {
                padding: 24px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                text-align: center;
            }

            header h1 {
                margin: 0;
                font-size: 36px;
            }

            header p {
                margin: 10px 0 0;
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
                background: #1e293b;
                padding: 20px;
                border-radius: 16px;
                border: 1px solid #334155;
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
                background: #1e293b;
                border: 1px solid #334155;
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
                border: 1px solid #475569;
                background: #0f172a;
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
                background: #6366f1;
                color: white;
            }

            .btn-danger {
                background: #ef4444;
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
                border-bottom: 1px solid #334155;
                text-align: left;
                font-size: 14px;
            }

            th {
                background: #334155;
                color: #cbd5e1;
            }

            tr:hover {
                background: #253449;
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
            <h1>EmployeeHub Dashboard 🚀</h1>
            <p>Browser UI is calling the FastAPI REST API using JavaScript fetch()</p>
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

                let url = '/api/v1/employees?';

                if (search) {
                    url += 'search=' + encodeURIComponent(search) + '&';
                }

                if (department) {
                    url += 'department=' + encodeURIComponent(department);
                }

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
        "message": "EmployeeHub Step 2 API is running successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/info")
def api_info():
    return {
        "project": "EmployeeHub CRUD Dashboard",
        "step": "Step 2",
        "version": "2.0.0",
        "storage": "in-memory",
        "features": [
            "FastAPI",
            "REST API",
            "CRUD",
            "Pydantic Validation",
            "Interactive Mini UI"
        ]
    }


# ============================================================
# CRUD Endpoints
# ============================================================

@app.get("/api/v1/employees")
def get_employees(
    search: Optional[str] = Query(None, description="Search by name, email, or employee code"),
    department: Optional[str] = Query(None, description="Filter by department"),
):
    """
    Return the list of employees.

    Optional query parameters:
    - search
    - department
    """

    filtered_employees = employees_db

    if search:
        search_lower = search.lower()

        filtered_employees = [
            employee for employee in filtered_employees
            if search_lower in employee["first_name"].lower()
            or search_lower in employee["last_name"].lower()
            or search_lower in employee["email"].lower()
            or search_lower in employee["employee_code"].lower()
        ]

    if department:
        department_lower = department.lower()

        filtered_employees = [
            employee for employee in filtered_employees
            if employee["department"].lower() == department_lower
        ]

    return {
        "total": len(filtered_employees),
        "employees": filtered_employees
    }


@app.get("/api/v1/employees/stats/summary")
def get_employee_stats():
    """
    Return employee summary statistics.
    """

    total_employees = len(employees_db)
    active_employees = len([employee for employee in employees_db if employee["is_active"]])

    if total_employees == 0:
        average_salary = 0
    else:
        total_salary = sum(employee["salary"] for employee in employees_db)
        average_salary = round(total_salary / total_employees, 2)

    department_counts = {}

    for employee in employees_db:
        department = employee["department"]

        if department not in department_counts:
            department_counts[department] = 0

        department_counts[department] += 1

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": total_employees - active_employees,
        "average_salary": average_salary,
        "department_counts": department_counts
    }


@app.post(
    "/api/v1/employees",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeResponse
)
def create_employee(employee_data: EmployeeCreate):
    """
    Create a new employee.
    """

    global next_employee_id

    if check_duplicate_employee_code(employee_data.employee_code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee code '{employee_data.employee_code}' already exists"
        )

    if check_duplicate_email(employee_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{employee_data.email}' already exists"
        )

    new_employee = {
        "id": next_employee_id,
        "employee_code": employee_data.employee_code,
        "first_name": employee_data.first_name,
        "last_name": employee_data.last_name,
        "email": employee_data.email,
        "department": employee_data.department,
        "designation": employee_data.designation,
        "salary": employee_data.salary,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
    }

    employees_db.append(new_employee)
    next_employee_id += 1

    return new_employee


@app.get(
    "/api/v1/employees/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(employee_id: int):
    """
    Return a single employee by ID.
    """

    employee = find_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )

    return employee


@app.put(
    "/api/v1/employees/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(employee_id: int, employee_data: EmployeeUpdate):
    """
    Update an existing employee.

    Only the fields provided in the request body will be updated.
    """

    employee = find_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )

    update_data = employee_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )

    if "email" in update_data:
        if check_duplicate_email(update_data["email"], ignore_employee_id=employee_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{update_data['email']}' already exists"
            )

    for field_name, field_value in update_data.items():
        employee[field_name] = field_value

    employee["updated_at"] = datetime.utcnow().isoformat()

    return employee


@app.delete("/api/v1/employees/{employee_id}")
def delete_employee(employee_id: int):
    """
    Delete an employee by ID.
    """

    employee = find_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )

    employees_db.remove(employee)

    return {
        "message": "Employee deleted successfully",
        "deleted_employee_id": employee_id
    }