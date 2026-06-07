import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.step_03_sqlite_crud import Base, app, get_db


TEST_DATABASE_URL = "sqlite:///./test_employeehub.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def override_get_db():
    """
    Provide a test database session for API tests.
    """

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """
    Create a fresh test database for each test.
    """

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def sample_employee():
    """
    Return sample employee payload.
    """

    return {
        "employee_code": "EMPTEST001",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "department": "data",
        "designation": "Data Engineer",
        "salary": 90000
    }


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "SQLite"


def test_get_employees_empty_list(client):
    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["employees"] == []


def test_create_employee(client, sample_employee):
    response = client.post("/api/v1/employees", json=sample_employee)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["employee_code"] == "EMPTEST001"
    assert data["first_name"] == "Test"
    assert data["email"] == "test.user@example.com"
    assert data["department"] == "data"
    assert data["salary"] == 90000


def test_create_duplicate_employee_code_returns_409(client, sample_employee):
    first_response = client.post("/api/v1/employees", json=sample_employee)
    assert first_response.status_code == 201

    second_response = client.post("/api/v1/employees", json=sample_employee)

    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


def test_create_duplicate_email_returns_409(client, sample_employee):
    first_response = client.post("/api/v1/employees", json=sample_employee)
    assert first_response.status_code == 201

    duplicate_email_payload = {
        **sample_employee,
        "employee_code": "EMPTEST002"
    }

    second_response = client.post("/api/v1/employees", json=duplicate_email_payload)

    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


def test_get_employee_by_id(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    employee_id = create_response.json()["id"]

    response = client.get(f"/api/v1/employees/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == employee_id
    assert data["employee_code"] == "EMPTEST001"


def test_get_employee_not_found_returns_404(client):
    response = client.get("/api/v1/employees/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_employee_salary(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    employee_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/employees/{employee_id}",
        json={
            "salary": 120000,
            "designation": "Senior Data Engineer"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()
    assert data["salary"] == 120000
    assert data["designation"] == "Senior Data Engineer"
    assert data["first_name"] == "Test"


def test_update_employee_empty_body_returns_400(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    employee_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/employees/{employee_id}",
        json={}
    )

    assert update_response.status_code == 400
    assert update_response.json()["detail"] == "No update data provided"


def test_delete_employee(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    employee_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/employees/{employee_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_employee_id"] == employee_id

    get_response = client.get(f"/api/v1/employees/{employee_id}")
    assert get_response.status_code == 404


def test_search_employee(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    assert create_response.status_code == 201

    response = client.get("/api/v1/employees?search=test")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["employees"][0]["employee_code"] == "EMPTEST001"


def test_department_filter(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    assert create_response.status_code == 201

    response = client.get("/api/v1/employees?department=data")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["employees"][0]["department"] == "data"


def test_negative_salary_validation_returns_422(client, sample_employee):
    sample_employee["salary"] = -5000

    response = client.post("/api/v1/employees", json=sample_employee)

    assert response.status_code == 422


def test_invalid_email_validation_returns_422(client, sample_employee):
    sample_employee["email"] = "invalid-email"

    response = client.post("/api/v1/employees", json=sample_employee)

    assert response.status_code == 422


def test_employee_stats(client, sample_employee):
    create_response = client.post("/api/v1/employees", json=sample_employee)
    assert create_response.status_code == 201

    response = client.get("/api/v1/employees/stats/summary")

    assert response.status_code == 200
    data = response.json()

    assert data["total_employees"] == 1
    assert data["active_employees"] == 1
    assert data["inactive_employees"] == 0
    assert data["average_salary"] == 90000
    assert data["department_counts"]["data"] == 1