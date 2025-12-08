"""API router for units"""
from fastapi import APIRouter, HTTPException
from database import get_session
from models import Unit

router = APIRouter()


@router.get("/by-property/{property_id:path}")
async def get_by_property(property_id: str):
    """Get units by property ID"""
    async with get_session() as session:
        units = list(session.query(object_type=Unit).where_equals("PropertyId", property_id))
        return units


@router.post("")
async def create(unit: Unit):
    """Create a new unit"""
    async with get_session() as session:
        if not unit.PropertyId or not unit.UnitNumber:
            raise HTTPException(status_code=400, detail="PropertyId and UnitNumber are required")
        
        unit.Id = f"{unit.PropertyId}/{unit.UnitNumber}"
        session.store(unit)
        session.save_changes()
        return unit
