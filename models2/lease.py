from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, date
from ravendb.tools.utils import Utils
from .base import EntityBase


@dataclass(eq=False)
class Lease(EntityBase):
    UnitId: str = ""
    RenterIds: list[str] = field(default_factory=list)
    LeaseAmount: float = 0.0
    StartDate: datetime = field(default_factory=datetime.now)
    EndDate: datetime = field(default_factory=datetime.now)
    LegalDocumentId: Optional[str] = None
    PowerUnitPrice: float = 0.12  # default $0.12 per kWh
    WaterUnitPrice: float = 0.005  # default $0.005 per gallon
    Id: Optional[str] = None
    
    @property
    def IsActive(self) -> bool:
        today = date.today()
        if isinstance(self.StartDate, str):
            self.StartDate = Utils.string_to_datetime(self.StartDate)
        if isinstance(self.EndDate, str):
            self.EndDate = Utils.string_to_datetime(self.EndDate)
        return self.StartDate.date() <= today <= self.EndDate.date()
    
    def as_dict(self) -> dict:
        data = self.__dict__.copy()
        data["IsActive"] = self.IsActive
        return data

    @classmethod
    def collection_name(cls) -> str:
        return "Leases"
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "Lease":
        # Remove RavenDB metadata
        json_dict.pop("@metadata", None)
        
        # Convert datetime strings to datetime objects
        if "StartDate" in json_dict and isinstance(json_dict["StartDate"], str):
            json_dict["StartDate"] = Utils.string_to_datetime(json_dict["StartDate"])
        if "EndDate" in json_dict and isinstance(json_dict["EndDate"], str):
            json_dict["EndDate"] = Utils.string_to_datetime(json_dict["EndDate"])
        
        return cls(**json_dict)
