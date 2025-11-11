from typing import List, Optional
from app.repositories.flight_repository import FlightRepository


class FlightService:
    """Handles all business logic for flights."""

    def __init__(self, repository: FlightRepository):
        self.repo = repository

    def create_flight(self, flight_data: dict) -> dict:
        # Prevent duplicate flight_number
        existing = self.repo.get_by_number(flight_data["flight_number"])
        if existing:
            raise ValueError(f"Flight {flight_data['flight_number']} already exists")
        return self.repo.create(flight_data)

    def get_flights(
        self,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "departure_time",
        sort_order: str = "asc",
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> List[dict]:
        """
        in real task we use condition in this file
        but we use repository pattern in repo file
        so we use IF command in repo file with pay attention
        to query approach
        """
        return self.repo.get_all(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            origin=origin,
            destination=destination,
            is_active=is_active,
            sort=True,
        )

    def get_flight_by_number(self, flight_number: str) -> Optional[dict]:
        return self.repo.get_by_number(flight_number)

    def update_flight(self, flight_number: str, update_data: dict) -> dict:
        return self.repo.update(flight_number, update_data)

    def deactivate_flight(self, flight_number: str) -> dict:
        return self.repo.deactivate(flight_number)
