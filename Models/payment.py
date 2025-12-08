from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class PaymentMethod:
    method: str = ""
    amount: Decimal = Decimal("0.00")
    details: str = ""


@dataclass
class PaymentAllocation:
    debt_item_id: str = ""
    amount_applied: Decimal = Decimal("0.00")
    renter_id: str = ""


@dataclass
class Payment:
    payment_date: datetime = field(default_factory=datetime.now)
    total_amount_received: Decimal = Decimal("0.00")
    payment_methods: list[PaymentMethod] = field(default_factory=list)
    allocation: list[PaymentAllocation] = field(default_factory=list)
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Payments"
