"""API router for renters"""
from fastapi import APIRouter
from database import get_session
from models import Renter

router = APIRouter()


@router.get("")
async def get_all():
    """Get all renters"""
    async with get_session() as session:
        renters = list(session.query(object_type=Renter))
        return renters


@router.post("")
async def create(renter: Renter):
    """Create a new renter"""
    async with get_session() as session:
        session.store(renter)
        session.save_changes()
        return renter
