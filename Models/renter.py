from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .base import EntityBase


@dataclass(eq=False)
class CreditCard(EntityBase):
    Last4Digits: str = ""
    Type: str = ""  # Visa, MasterCard, Amex, Discover
    Expiration: str = ""  # MM/YY format


@dataclass(eq=False)
class Renter(EntityBase):
    FirstName: str = ""
    LastName: str = ""
    ContactEmail: str = ""
    ContactPhone: str = ""
    TelegramChatId: Optional[str] = None
    CreditCards: list[CreditCard] = field(default_factory=list)
    Id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Renters"
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "Renter":
        # Remove RavenDB metadata
        json_dict.pop("@metadata", None)
        
        # Convert CreditCards dicts to CreditCard objects
        credit_cards = json_dict.get("CreditCards", [])
        if credit_cards:
            json_dict["CreditCards"] = [
                CreditCard(**card) if isinstance(card, dict) else card
                for card in credit_cards
            ]
        
        return cls(**json_dict)
