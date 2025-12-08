from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Unit:
    PropertyId: str = ""
    UnitNumber: str = ""
    VacantFrom: Optional[datetime] = None
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Units"
