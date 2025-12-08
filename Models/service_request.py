from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ServiceRequest:
    RenterId: str = ""
    Type: str = ""
    Description: str = ""
    Status: str = "Open"
    OpenedAt: datetime = field(default_factory=datetime.now)
    UnitId: Optional[str] = None
    PropertyId: Optional[str] = None
    ClosedAt: Optional[datetime] = None
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "ServiceRequests"
