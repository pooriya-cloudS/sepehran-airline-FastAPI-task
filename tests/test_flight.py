from app.repositories.flight_repository import FlightRepository
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

DATABASE_URL = "mysql+pymysql://appuser1:MyPass123!@127.0.0.1:3306/mydb"
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

repo = FlightRepository(db)


def test_create_flight():
    flight = {
        "id": str(uuid.uuid4()),
        "flight_number": "TEST101",
        "origin": "Tehran",
        "destination": "Mashhad",
        "departure_time": "2025-11-10 09:00:00",
        "arrival_time": "2025-11-10 11:00:00",
    }
    created = repo.create(flight)
    assert created["flight_number"] == "TEST101"
