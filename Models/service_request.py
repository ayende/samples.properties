from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from .base import EntityBase


@dataclass(eq=False)
class ServiceRequest(EntityBase):
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
