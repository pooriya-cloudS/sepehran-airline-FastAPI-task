import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.flight_model import Base
import os
import pytest
from app.api.routers.flights_router import (
    get_db,
)

# ======================================================
# TEST DATABASE CONFIGURATION
# ======================================================

# SQLite database (stored locally for testing only)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create engine and session factory
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ======================================================
# DATABASE SETUP AND TEARDOWN
# ======================================================
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create a clean database schema before each test and remove it afterward."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ======================================================
# OVERRIDE DEPENDENCY FOR TESTING
# ======================================================
def override_get_db():
    """Provide a testing session instead of the production DB session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the dependency override to the FastAPI app
app.dependency_overrides[get_db] = override_get_db


# ======================================================
# TEST CLIENT FIXTURE
# ======================================================
@pytest.fixture
def client():
    """Return a FastAPI TestClient instance."""
    return TestClient(app)


# ======================================================
# SCENARIO 1: Create a new flight successfully
# ======================================================
def test_create_flight_success(client):
    flight_data = {
        "flight_number": "IR125",
        "origin": "Tehran",
        "destination": "Istanbul",
        "departure_time": "2025-11-12T08:00:00",
        "arrival_time": "2025-11-12T10:30:00",
    }
    response = client.post("/flights/create/", json=flight_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Flight created successfully"


# ======================================================
# SCENARIO 2: Retrieve paginated and sorted flight list
# ======================================================
def test_get_paginated_sorted_flights(client):
    # Create multiple flights
    for i in range(1, 6):
        client.post(
            "/flights/create/",
            json={
                "flight_number": f"IR10{i}",
                "origin": "Tehran",
                "destination": "Mashhad",
                "departure_time": f"2025-11-12T0{i}:00:00",
                "arrival_time": f"2025-11-12T1{i}:00:00",
            },
        )

    response = client.get("/flights/?page=1&limit=5&sort_by=departure_time")
    assert response.status_code == 200
    flights = response.json()["data"]
    assert len(flights) <= 5
    times = [f["departure_time"] for f in flights]
    assert times == sorted(times)


# ======================================================
# SCENARIO 3: Filter flights by origin city
# ======================================================
def test_filter_flights_by_origin(client):
    client.post(
        "/flights/create/",
        json={
            "flight_number": "IR200",
            "origin": "Tehran",
            "destination": "Shiraz",
            "departure_time": "2025-11-13T08:00:00",
            "arrival_time": "2025-11-13T10:00:00",
        },
    )
    client.post(
        "/flights/create/",
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


# ======================================================
# SCENARIO 4: Update an existing flight record
# ======================================================
def test_update_flight(client):
    client.post(
        "/flights/create/",
        json={
            "flight_number": "IR123",
            "origin": "Tehran",
            "destination": "Istanbul",
            "departure_time": "2025-11-12T08:00:00",
            "arrival_time": "2025-11-12T10:30:00",
        },
    )

    update_data = {
        "flight_number": "IR123",
        "origin": "Tehran",
        "destination": "Ankara",
        "departure_time": "2025-11-12T08:00:00",
        "arrival_time": "2025-11-12T10:30:00",
    }
    response = client.put("/flights/IR123", json=update_data)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["destination"] == "Ankara"
    assert data["message"] == "Flight updated successfully"


# ======================================================
# SCENARIO 5: Deactivate a flight instead of deleting it
# ======================================================
def test_deactivate_flight(client):
    client.post(
        "/flights/create/",
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

    # Verify the is_active flag
    check = client.get("/flights/IR123")
    assert check.json()["data"]["is_active"] == 0


# ======================================================
# SCENARIO 6: Handle invalid flight creation request
# ======================================================
def test_invalid_flight_creation(client):
    invalid_data = {"flight_number": "IR999", "origin": "Tehran"}
    response = client.post("/flights/create/", json=invalid_data)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    if os.path.exists("test.db"):
        os.remove("test.db")
