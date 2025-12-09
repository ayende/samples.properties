from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from ravendb.tools.utils import Utils
from .base import EntityBase


@dataclass(eq=False)
class Unit(EntityBase):
    PropertyId: str = ""
    UnitNumber: str = ""
    VacantFrom: Optional[datetime] = None
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Units"
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "Unit":
        # Remove RavenDB metadata
        json_dict.pop("@metadata", None)
        
        # Convert datetime strings
        if "VacantFrom" in json_dict and isinstance(json_dict["VacantFrom"], str):
            json_dict["VacantFrom"] = Utils.string_to_datetime(json_dict["VacantFrom"])
        
        return cls(**json_dict)
