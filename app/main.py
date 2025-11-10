from fastapi import FastAPI
from app.api.routers.flights_router import router as flights_router

# Initialize FastAPI app
app = FastAPI(
    title="Sepehran Airline API",
    description="Flight management system with CRUD operations and soft deletion.",
    version="1.0.0"
)

# Include flight routes
app.include_router(flights_router, prefix="/flights", tags=["Flights"])


@app.get("/")
def root():
    """Root endpoint for health check."""
    return {"message": "Sepehran Airline API is running 🚀"}
