from dataclasses import dataclass
from typing import Optional
from datetime import datetime
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
