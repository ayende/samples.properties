from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class PaymentMethod:
    Method: str = ""
    Amount: Decimal = Decimal("0.00")
    Details: str = ""


@dataclass
class PaymentAllocation:
    DebtItemId: str = ""
    AmountApplied: Decimal = Decimal("0.00")
    RenterId: str = ""


@dataclass
class Payment:
    PaymentDate: datetime = field(default_factory=datetime.now)
    TotalAmountReceived: Decimal = Decimal("0.00")
    PaymentMethods: list[PaymentMethod] = field(default_factory=list)
    Allocation: list[PaymentAllocation] = field(default_factory=list)
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Payments"
