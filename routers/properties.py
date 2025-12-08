"""API router for properties"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from database import get_session
from models import Property, Unit

router = APIRouter()


@router.get("")
async def get_all(bounds_wkt: Optional[str] = None):
    """Get all properties, optionally filtered by spatial bounds"""
    async with get_session() as session:
        # Build query for properties
        query = session.query(object_type=Property)
        
        # Apply spatial filtering if bounds provided
        if bounds_wkt:
            query = query.spatial(
                lambda x: x.point("Latitude", "Longitude"),
                lambda criteria: criteria.relates_to_shape(bounds_wkt, "Within")
            )
        
        properties = list(query)
        
        # Get all unit IDs for these properties
        property_ids = [p.Id for p in properties]
        units = list(
            session.query(object_type=Unit).where_in("PropertyId", property_ids)
        )
        
        # Group units by property ID
        units_by_property = {}
        for unit in units:
            if unit.PropertyId not in units_by_property:
                units_by_property[unit.PropertyId] = []
            units_by_property[unit.PropertyId].append(unit)
        
        # Build result
        result = []
        for prop in properties:
            result.append({
                "Id": prop.Id,
                "Name": prop.Name,
                "Address": prop.Address,
                "TotalUnits": prop.TotalUnits,
                "Latitude": prop.Latitude,
                "Longitude": prop.Longitude,
                "Units": units_by_property.get(prop.Id, [])
            })
        
        return result


@router.post("")
async def create(property: Property):
    """Create a new property"""
    async with get_session() as session:
        session.store(property)
        session.save_changes()
        return property
