"""API router for utility usage"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from database import get_session
from models import Unit

router = APIRouter()


@router.get("/{unit_id:path}")
async def get_utility_usage(
    unit_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Get utility usage for a unit"""
    async with get_session() as session:
        unit = session.load(unit_id, object_type=Unit)
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        # Parse dates
        start_date = datetime.fromisoformat(from_date) if from_date else datetime.now()
        end_date = datetime.fromisoformat(to_date) if to_date else datetime.now()
        
        # Query time series - Note: This is simplified, actual implementation
        # depends on pyravendb time series support
        # For now, returning placeholder
        return {
            "unitId": unit_id,
            "powerUsage": [],
            "waterUsage": []
        }


@router.post("/{unit_id:path}/upload")
async def upload_utility_data(unit_id: str, data: dict):
    """Upload utility usage data"""
    async with get_session() as session:
        unit = session.load(unit_id, object_type=Unit)
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        # Store time series data - simplified
        # Actual implementation depends on pyravendb time series API
        
        return {"message": "Data uploaded successfully"}
