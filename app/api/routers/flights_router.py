from fastapi import APIRouter, HTTPException

# Create router instance
router = APIRouter()

# Base placeholder route to ensure router loads correctly
@router.get("/")
async def get_flights_placeholder():
    """Temporary placeholder to make router importable."""
    raise HTTPException(status_code=501, detail="Not Implemented")
