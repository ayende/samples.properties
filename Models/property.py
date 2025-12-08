from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Property:
    name: str = ""
    address: str = ""
    total_units: int = 0
    latitude: float = 0.0
    longitude: float = 0.0
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Properties"
