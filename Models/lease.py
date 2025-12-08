from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


@dataclass
class Lease:
    unit_id: str = ""
    renter_ids: list[str] = field(default_factory=list)
    lease_amount: Decimal = Decimal("0.00")
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    legal_document_id: Optional[str] = None
    power_unit_price: Decimal = Decimal("0.12")  # default $0.12 per kWh
    water_unit_price: Decimal = Decimal("0.005")  # default $0.005 per gallon
    id: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        today = date.today()
        return self.start_date.date() <= today <= self.end_date.date()
    
    @classmethod
    def collection_name(cls) -> str:
        return "Leases"
