from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CreditCard:
    Last4Digits: str = ""
    Type: str = ""  # Visa, MasterCard, Amex, Discover
    Expiration: str = ""  # MM/YY format


@dataclass
class Renter:
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
