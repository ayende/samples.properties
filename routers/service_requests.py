"""API router for service requests"""
from fastapi import APIRouter
from database import get_session
from models import ServiceRequest

router = APIRouter()


@router.get("")
async def get_all():
    """Get all service requests"""
    async with get_session() as session:
        requests = list(session.query(object_type=ServiceRequest))
        return requests


@router.post("")
async def create(service_request: ServiceRequest):
    """Create a new service request"""
    async with get_session() as session:
        session.store(service_request)
        session.save_changes()
        return service_request


@router.put("/status/{request_id:path}")
async def update_status(request_id: str, status: str):
    """Update service request status"""
    async with get_session() as session:
        service_request = session.load(request_id, object_type=ServiceRequest)
        if not service_request:
            raise HTTPException(status_code=404, detail="Service request not found")
        
        service_request.status = status
        session.save_changes()
        return service_request
