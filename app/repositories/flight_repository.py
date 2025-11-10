from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, text
from typing import List, Optional
import uuid


class FlightRepository:
    """
    Repository class for managing Flight data.
    All database interactions are done via raw SQL queries.
    """

    def __init__(self, db: Session):
        self.db = db

    # ================= Create =================
    def create(self, flight_data: dict) -> dict:
        """
        Insert a new flight record into the database with UUID id.
        """
        flight_data = flight_data.copy()
        flight_data["id"] = str(uuid.uuid4())  # Generate UUID string
        existing = self.get_by_number(flight_data["flight_number"])

        if existing:
            raise ValueError(
                f"Flight with number {flight_data['flight_number']} already exists"
            )

        query = """
        INSERT INTO flights (id, flight_number, origin, destination, departure_time, arrival_time, is_active)
        VALUES (:id, :flight_number, :origin, :destination, :departure_time, :arrival_time, 1)
        """
        self.db.execute(text(query), flight_data)
        self.db.commit()
        return flight_data

    # ================= Read / List =================
    def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "departure_time",
        sort_order: str = "asc",
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        is_active: Optional[bool] = True,
        sort: bool = False,
    ) -> List[dict]:
        base_query = "SELECT * FROM flights WHERE 1=1"
        params = {}

        if origin:
            base_query += " AND origin = :origin"
            params["origin"] = origin
        if destination:
            base_query += " AND destination = :destination"
            params["destination"] = destination
        if is_active is not None:
            base_query += " AND is_active = :is_active"
            params["is_active"] = is_active

        if sort:
            base_query += f" ORDER BY {sort_by} {sort_order.upper()}"

        offset = (page - 1) * limit
        base_query += " LIMIT :limit OFFSET :offset"
        params.update({"limit": limit, "offset": offset})

        result = self.db.execute(text(base_query), params).mappings().all()
        return [dict(row) for row in result]

    # ================= Get by Flight Number =================
    def get_by_number(self, flight_number: str) -> Optional[dict]:
        query = "SELECT * FROM flights WHERE flight_number = :flight_number"
        result = (
            self.db.execute(text(query), {"flight_number": flight_number})
            .mappings()
            .first()
        )
        return dict(result) if result else None

    # ================= Update =================
    def update(self, flight_number: str, update_data: dict) -> Optional[dict]:
        if not update_data:
            return None

        set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        update_data["flight_number"] = flight_number
        query = f"UPDATE flights SET {set_clause} WHERE flight_number = :flight_number"
        self.db.execute(text(query), update_data)
        self.db.commit()
        return self.get_by_number(flight_number)

    # ================= Deactivate =================
    def deactivate(self, flight_number: str) -> Optional[dict]:
        query = """
        UPDATE flights
        SET is_active = 0
        WHERE flight_number = :flight_number AND is_active = 1
        """
        self.db.execute(text(query), {"flight_number": flight_number})
        self.db.commit()
        return self.get_by_number(flight_number)

    # ================= "Delete" =================
    def delete(self, flight_number: str) -> Optional[dict]:
        return self.deactivate(flight_number)


# ====== Database setup ======
DATABASE_URL = "mysql+pymysql://appuser1:MyPass123!@127.0.0.1:3306/mydb"
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# ====== Create table if not exists ======
create_table_query = """
CREATE TABLE IF NOT EXISTS flights (
    id VARCHAR(36) PRIMARY KEY,
    flight_number VARCHAR(10),
    origin VARCHAR(50),
    destination VARCHAR(50),
    departure_time DATETIME,
    arrival_time DATETIME,
    is_active TINYINT(1) DEFAULT 1
)
"""
db.execute(text(create_table_query))
db.commit()

# ====== Test FlightRepository ======
repo = FlightRepository(db)

flight = {
    "flight_number": "IR101",
    "origin": "Tehran",
    "destination": "Mashhad",
    "departure_time": "2025-11-10 09:00:00",
    "arrival_time": "2025-11-10 11:00:00",
}

created = repo.create(flight)
print("Created:", created)

all_flights = repo.get_all(sort=True)
print("All Flights:", all_flights)

single_flight = repo.get_by_number("IR101")
print("Single Flight:", single_flight)

updated_flight = repo.update("IR101", {"origin": "Shiraz"})
print("Updated Flight:", updated_flight)

deactivated_flight = repo.deactivate("IR101")
print("Deactivated Flight:", deactivated_flight)
