from sqlalchemy import Column, String, DateTime, Boolean
from ..database import Base
from uuid import uuid4


class Flight(Base):
    __tablename__ = "flights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), nullable=False, index=True)
    flight_number = Column(String(10), unique=True)
    origin = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
