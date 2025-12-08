"""API router for service requests"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_session
from models import ServiceRequest, Property, Unit


class UpdateStatusRequest(BaseModel):
    Status: str


router = APIRouter()


@router.post("")
async def create(service_request: ServiceRequest):
    """Create a new service request"""
    async with get_session() as session:
        session.store(service_request)
        session.save_changes()
        return service_request


@router.get("/status/{status}")
async def get_by_status(status: str, boundsWkt: Optional[str] = None):
    """Get service requests by status, optionally filtered by spatial bounds"""
    async with get_session() as session:
        # Query service requests by status
        query = session.query_index("ServiceRequests/ByStatusAndLocation", object_type=ServiceRequest).where_equals("Status", status)
        query = query.include("PropertyId").include("UnitId")
        
        # Apply spatial filtering if bounds provided
        if boundsWkt:
            query = query.spatial("Location", lambda x: x.within(boundsWkt))
        
        # Order by opened date descending and limit to 10
        requests = list(query.order_by_descending("OpenedAt").take(10))
        
        # Build result with related data
        result = []
        for req in requests:
            # Load property and unit details
            property_name = None
            if req.PropertyId:
                prop = session.load(req.PropertyId, object_type=Property)
                property_name = prop.Name if prop else None
            
            unit_number = None
            if req.UnitId:
                unit = session.load(req.UnitId, object_type=Unit)
                unit_number = unit.UnitNumber if unit else None
            
            result.append({
                "Id": req.Id,
                "Status": req.Status,
                "OpenedAt": req.OpenedAt,
                "UnitId": req.UnitId,
                "PropertyId": req.PropertyId,
                "Type": req.Type,
                "Description": req.Description,
                "PropertyName": property_name,
                "UnitNumber": unit_number
            })
        
        return result


@router.put("/status/{request_id:path}")
async def update_status(request_id: str, update_request: UpdateStatusRequest):
    """Update service request status"""
    async with get_session() as session:
        service_request = session.load(request_id, object_type=ServiceRequest)
        if not service_request:
            raise HTTPException(status_code=404, detail="Service request not found")
        
        service_request.Status = update_request.Status
        
        # Set ClosedAt if status is Closed or Canceled
        if update_request.Status in ("Closed", "Canceled"):
            service_request.ClosedAt = datetime.today().date()
        
        session.save_changes()
        return service_request
