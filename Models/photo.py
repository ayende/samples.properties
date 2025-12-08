from dataclasses import dataclass
from typing import Optional


@dataclass
class Photo:
    conversation_id: str = ""
    renter_id: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Photos"
