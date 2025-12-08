"""API router for leases"""
from fastapi import APIRouter
from database import get_session
from models import Lease

router = APIRouter()


@router.get("")
async def get_all():
    """Get all leases"""
    async with get_session() as session:
        leases = list(session.query(object_type=Lease))
        return leases


@router.post("")
async def create(lease: Lease):
    """Create a new lease"""
    async with get_session() as session:
        session.store(lease)
        session.save_changes()
        return lease
