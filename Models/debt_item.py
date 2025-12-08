from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
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
