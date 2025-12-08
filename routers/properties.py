"""API router for properties"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from database import get_session
from models import Property, Unit

router = APIRouter()


@router.get("")
async def get_all(bounds_wkt: Optional[str] = None):
    """Get all properties, optionally filtered by spatial bounds"""
    async with get_session() as session:
        query = session.query(object_type=Property)
        
        if bounds_wkt:
            # Apply spatial filtering
            query = query.spatial(
                lambda x: x.point(lambda p: p.latitude, lambda p: p.longitude),
                lambda criteria: criteria.relates_to_shape(bounds_wkt, "Within")
            )
        
        properties = list(query)
        property_ids = [p.id for p in properties]
        
        # Load units for these properties
        units = list(session.query(object_type=Unit).where_in("property_id", property_ids))
        
        units_by_property = {}
        for unit in units:
            if unit.property_id not in units_by_property:
                units_by_property[unit.property_id] = []
            units_by_property[unit.property_id].append(unit)
        
        # Build result
        result = []
        for prop in properties:
            result.append({
                "id": prop.id,
                "name": prop.name,
                "address": prop.address,
                "totalUnits": prop.total_units,
                "latitude": prop.latitude,
                "longitude": prop.longitude,
                "units": units_by_property.get(prop.id, [])
            })
        
        return result


@router.post("")
async def create(property: Property):
    """Create a new property"""
    async with get_session() as session:
        session.store(property)
        session.save_changes()
        return property
