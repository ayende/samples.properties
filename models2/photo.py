from dataclasses import dataclass
from typing import Optional
from .base import EntityBase


@dataclass(eq=False)
class Photo(EntityBase):
    ConversationId: str = ""
    RenterId: Optional[str] = None
    Caption: Optional[str] = None
    Description: Optional[str] = None
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Photos"
