from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from ravendb.tools.utils import Utils
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
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "Payment":
        # Remove RavenDB metadata
        json_dict.pop("@metadata", None)
        
        # Convert datetime strings
        if "PaymentDate" in json_dict and isinstance(json_dict["PaymentDate"], str):
            json_dict["PaymentDate"] = Utils.string_to_datetime(json_dict["PaymentDate"])
        
        # Convert PaymentMethods dicts to objects
        payment_methods = json_dict.get("PaymentMethods", [])
        if payment_methods:
            json_dict["PaymentMethods"] = [
                PaymentMethod(**pm) if isinstance(pm, dict) else pm
                for pm in payment_methods
            ]
        
        # Convert Allocation dicts to objects
        allocation = json_dict.get("Allocation", [])
        if allocation:
            json_dict["Allocation"] = [
                PaymentAllocation(**pa) if isinstance(pa, dict) else pa
                for pa in allocation
            ]
        
        return cls(**json_dict)
