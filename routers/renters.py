"""API router for renters"""
from fastapi import APIRouter
from database import get_session
from models import Renter

router = APIRouter()


@router.get("/{renter_id}")
async def get_by_id(renter_id: str):
    """Get a renter by ID"""
    async with get_session() as session:
        renter = session.load(renter_id, object_type=Renter)
        if not renter:
            return {"error": "Renter not found"}
        return renter


@router.post("")
async def create(renter: Renter):
    """Create a new renter"""
    async with get_session() as session:
        session.store(renter)
        session.save_changes()
        return renter
