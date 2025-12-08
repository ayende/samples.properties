"""API router for debt items"""
from fastapi import APIRouter
from database import get_session
from models import DebtItem

router = APIRouter()


@router.get("")
async def get_all():
    """Get all debt items"""
    async with get_session() as session:
        debt_items = list(session.query(object_type=DebtItem))
        return debt_items


@router.post("")
async def create(debt_item: DebtItem):
    """Create a new debt item"""
    async with get_session() as session:
        session.store(debt_item)
        session.save_changes()
        return debt_item
