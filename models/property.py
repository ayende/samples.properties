from dataclasses import dataclass, field
from typing import Optional
from .base import EntityBase


@dataclass(eq=False)
class Property(EntityBase):
    Name: str = ""
    Address: str = ""
    TotalUnits: int = 0
    Latitude: float = 0.0
    Longitude: float = 0.0
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Properties"
