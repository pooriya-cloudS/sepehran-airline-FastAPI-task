from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FlightBase(BaseModel):
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    flight_number: Optional[str]
    origin: Optional[str]
    destination: Optional[str]
    departure_time: Optional[datetime]
    arrival_time: Optional[datetime]


class FlightOut(FlightBase):
    id: str
    is_active: bool

    class Config:
        orm_mode = True
