from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Unit:
    property_id: str = ""
    unit_number: str = ""
    vacant_from: Optional[datetime] = None
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Units"
