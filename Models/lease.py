from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


@dataclass
class Lease:
    UnitId: str = ""
    RenterIds: list[str] = field(default_factory=list)
    LeaseAmount: Decimal = Decimal("0.00")
    StartDate: datetime = field(default_factory=datetime.now)
    EndDate: datetime = field(default_factory=datetime.now)
    LegalDocumentId: Optional[str] = None
    PowerUnitPrice: Decimal = Decimal("0.12")  # default $0.12 per kWh
    WaterUnitPrice: Decimal = Decimal("0.005")  # default $0.005 per gallon
    Id: Optional[str] = None
    
    @property
    def IsActive(self) -> bool:
        today = date.today()
        return self.StartDate.date() <= today <= self.EndDate.date()
    
    @classmethod
    def collection_name(cls) -> str:
        return "Leases"
