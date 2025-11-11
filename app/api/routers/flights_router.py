from fastapi import APIRouter, HTTPException, status
from app.schemas.flight_schema import FlightCreate, FlightUpdate
from app.services.flight_service import FlightService
from app.repositories.flight_repository import FlightRepository
from app.database import get_db
from fastapi import Depends

router = APIRouter()


def create_service(db):
    flight_repo = FlightRepository(db)
    service = FlightService(flight_repo)
    return service


@router.post("/create/", status_code=status.HTTP_201_CREATED)
def create_flight(flight: FlightCreate, db=Depends(get_db)):
    try:
        service = create_service(db)
        result = service.create_flight(flight.dict())
        return {
            "status": "success",
            "message": "Flight created successfully",
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def list_flights(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "departure_time",
    sort_order: str = "asc",
    origin: str = None,
    destination: str = None,
    db=Depends(get_db),
):
    service = create_service(db)

    result = service.get_flights(page, limit, sort_by, sort_order, origin, destination)
    return {"status": "success", "data": result}


@router.get("/{flight_number}")
def get_flight(flight_number: str, db=Depends(get_db)):
    service = create_service(db)

    result = service.get_flight_by_number(flight_number)
    if not result:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"status": "success", "data": result}


@router.put("/{flight_number}")
def update_flight(flight_number: str, flight: FlightUpdate, db=Depends(get_db)):
    service = create_service(db)

    result = service.update_flight(flight_number, flight.dict(exclude_unset=True))
    return {
        "status": "success",
        "message": "Flight updated successfully",
        "data": result,
    }


@router.patch("/{flight_number}/deactivate")
def deactivate_flight(flight_number: str, db=Depends(get_db)):
    service = create_service(db)

    result = service.deactivate_flight(flight_number)
    return {
        "status": "success",
        "message": "Flight deactivated successfully",
        "data": result,
    }
