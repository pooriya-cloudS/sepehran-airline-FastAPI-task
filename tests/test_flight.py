import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.flight_model import Base  # ← make sure Base imported from your models


# ==========================
# DATABASE CONFIGURATION
# ==========================

# Main DB URL (without test_db)
MAIN_DATABASE_URL = "mysql+pymysql://appuser1:MyPass123!@127.0.0.1:3306"

# Test DB name
TEST_DB_NAME = "test_db"

# Create engine for root (for creating and dropping test_db)
root_engine = create_engine(MAIN_DATABASE_URL, isolation_level="AUTOCOMMIT")

# Test DB full URL
TEST_DATABASE_URL = f"{MAIN_DATABASE_URL}/{TEST_DB_NAME}"

# Test engine & session
engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create and drop test database for the test session."""
    # Drop if exists
    with root_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(
            text(
                f"CREATE DATABASE {TEST_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )

    # Create tables
    Base.metadata.create_all(bind=engine)

    yield  # ---- Run the tests ----

    # Cleanup: drop the test database
    with root_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))


@pytest.fixture(scope="function", autouse=True)
def clean_tables():
    """Clean all tables before each test."""
    db = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()
    yield


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    return TestClient(app)


# ===================================================
# Scenario: Create a new flight record successfully
# ===================================================
def test_create_flight_success(client):
    flight_data = {
        "flight_number": "IR123",
        "origin": "Tehran",
        "destination": "Istanbul",
        "departure_time": "2025-11-12T08:00:00",
        "arrival_time": "2025-11-12T10:30:00",
    }

    response = client.post("/flights/", json=flight_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Flight created successfully"


# ===================================================
# Scenario: Retrieve paginated and sorted list
# ===================================================
def test_get_paginated_sorted_flights(client):
    for i in range(1, 4):
        client.post(
            "/flights/",
            json={
                "flight_number": f"IR10{i}",
                "origin": "Tehran",
                "destination": "Mashhad",
                "departure_time": f"2025-11-12T0{i}:00:00",
                "arrival_time": f"2025-11-12T1{i}:00:00",
            },
        )

    response = client.get("/flights/?page=1&limit=2&sort_by=departure_time")
    assert response.status_code == 200
    flights = response.json()["data"]
    assert len(flights) <= 2

    times = [f["departure_time"] for f in flights]
    assert times == sorted(times)


# ===================================================
# Scenario: Filter flights by origin
# ===================================================
def test_filter_flights_by_origin(client):
    client.post(
        "/flights/",
        json={
            "flight_number": "IR200",
            "origin": "Tehran",
            "destination": "Shiraz",
            "departure_time": "2025-11-13T08:00:00",
            "arrival_time": "2025-11-13T10:00:00",
        },
    )
    client.post(
        "/flights/",
        json={
            "flight_number": "IR201",
            "origin": "Tabriz",
            "destination": "Tehran",
            "departure_time": "2025-11-13T11:00:00",
            "arrival_time": "2025-11-13T13:00:00",
        },
    )

    response = client.get("/flights/?origin=Tehran")
    assert response.status_code == 200
    flights = response.json()["data"]
    assert all(f["origin"] == "Tehran" for f in flights)


# ===================================================
# Scenario: Update an existing flight record
# ===================================================
def test_update_flight(client):
    client.post(
        "/flights/",
        json={
            "flight_number": "IR123",
            "origin": "Tehran",
            "destination": "Istanbul",
            "departure_time": "2025-11-12T08:00:00",
            "arrival_time": "2025-11-12T10:30:00",
        },
    )

    response = client.put("/flights/IR123", json={"destination": "Ankara"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Flight updated successfully"
    assert data["data"]["destination"] == "Ankara"


# ===================================================
# Scenario: Deactivate a flight instead of deleting
# ===================================================
def test_deactivate_flight(client):
    client.post(
        "/flights/",
        json={
            "flight_number": "IR123",
            "origin": "Tehran",
            "destination": "Istanbul",
            "departure_time": "2025-11-12T08:00:00",
            "arrival_time": "2025-11-12T10:30:00",
        },
    )

    response = client.patch("/flights/IR123/deactivate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Flight deactivated successfully"

    check = client.get("/flights/IR123")
    assert check.json()["data"]["is_active"] is False


# ===================================================
# Scenario: Invalid flight creation (validation error)
# ===================================================
def test_invalid_flight_creation(client):
    invalid_data = {"flight_number": "IR999", "origin": "Tehran"}
    response = client.post("/flights/", json=invalid_data)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
