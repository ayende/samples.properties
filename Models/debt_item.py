from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class DebtItem:
    type: str = ""
    description: str = ""
    amount_due: Decimal = Decimal("0.00")
    amount_paid: Decimal = Decimal("0.00")
    due_date: datetime = field(default_factory=datetime.now)
    lease_id: Optional[str] = None
    renter_id: Optional[str] = None
    property_id: Optional[str] = None
    unit_id: Optional[str] = None
    renter_ids: list[str] = field(default_factory=list)
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "DebtItems"
