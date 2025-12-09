from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from ravendb.tools.utils import Utils
from .base import EntityBase


@dataclass(eq=False)
class DebtItem(EntityBase):
    Type: str = ""
    Description: str = ""
    AmountDue: float = 0.0
    AmountPaid: float = 0.0
    DueDate: datetime = field(default_factory=datetime.now)
    LeaseId: Optional[str] = None
    RenterId: Optional[str] = None
    PropertyId: Optional[str] = None
    UnitId: Optional[str] = None
    RenterIds: list[str] = field(default_factory=list)
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "DebtItems"
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "DebtItem":
        # Remove RavenDB metadata
        json_dict.pop("@metadata", None)
        
        # Convert datetime strings
        if "DueDate" in json_dict and isinstance(json_dict["DueDate"], str):
            json_dict["DueDate"] = Utils.string_to_datetime(json_dict["DueDate"])
        
        return cls(**json_dict)
