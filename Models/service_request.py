from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from ravendb.tools.utils import Utils
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
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "ServiceRequest":
        # Remove RavenDB metadata
        json_dict.pop("@metadata", None)
        
        # Convert datetime strings
        if "OpenedAt" in json_dict and isinstance(json_dict["OpenedAt"], str):
            json_dict["OpenedAt"] = Utils.string_to_datetime(json_dict["OpenedAt"])
        if "ClosedAt" in json_dict and isinstance(json_dict["ClosedAt"], str):
            json_dict["ClosedAt"] = Utils.string_to_datetime(json_dict["ClosedAt"])
        
        return cls(**json_dict)
