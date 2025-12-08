"""API router for leases"""
from datetime import datetime
from fastapi import APIRouter
from database import get_session
from models import Lease, Unit

router = APIRouter()


@router.post("")
async def create(lease: Lease):
    """Create a new lease"""
    async with get_session() as session:
        # Validate unit exists
        unit = session.load(lease.UnitId, object_type=Unit)
        if not unit:
            return {"error": "Unit not found"}
        
        # Store lease and clear unit's vacant status
        session.store(lease)
        unit.VacantFrom = None
        session.save_changes()
        return lease


@router.put("/{lease_id}/terminate")
async def terminate(lease_id: str):
    """Terminate a lease"""
    async with get_session() as session:
        # Load lease with unit included
        lease = session.include("UnitId").load(lease_id, object_type=Lease)
        if not lease:
            return {"error": "Lease not found"}
        
        # Load unit (no server call due to include)
        unit = session.load(lease.UnitId, object_type=Unit)
        if not unit:
            return {"error": "Unit not found"}
        
        # Set end date and mark unit as vacant
        lease.EndDate = datetime.today().date()
        unit.VacantFrom = datetime.today().date()
        
        session.save_changes()
        return lease


@router.get("/by-unit/{unit_id:path}")
async def get_by_unit(unit_id: str):
    """Get active lease for a unit"""
    async with get_session() as session:
        today = datetime.today().date()
        
        # Query for active lease
        lease = (session.query(object_type=Lease)
                 .where_equals("UnitId", unit_id)
                 .where_greater_than_or_equal("EndDate", today)
                 .where_less_than_or_equal("StartDate", today)
                 .first_or_default())
            
    
        if not lease:
            return {"error": "Lease not found"}
        
        return lease
