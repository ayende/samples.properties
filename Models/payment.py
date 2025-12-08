from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from .base import EntityBase


@dataclass(eq=False)
class PaymentMethod(EntityBase):
    Method: str = ""
    Amount: float = 0.0
    Details: str = ""


@dataclass(eq=False)
class PaymentAllocation(EntityBase):
    DebtItemId: str = ""
    AmountApplied: float = 0.0
    RenterId: str = ""


@dataclass(eq=False)
class Payment(EntityBase):
    PaymentDate: datetime = field(default_factory=datetime.now)
    TotalAmountReceived: float = 0.0
    PaymentMethods: list[PaymentMethod] = field(default_factory=list)
    Allocation: list[PaymentAllocation] = field(default_factory=list)
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Payments"
