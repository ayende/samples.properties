from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ServiceRequest:
    renter_id: str = ""
    type: str = ""
    description: str = ""
    status: str = "Open"
    opened_at: datetime = field(default_factory=datetime.now)
    unit_id: Optional[str] = None
    property_id: Optional[str] = None
    closed_at: Optional[datetime] = None
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "ServiceRequests"
