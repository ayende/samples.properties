from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CreditCard:
    last_4_digits: str = ""
    type: str = ""  # Visa, MasterCard, Amex, Discover
    expiration: str = ""  # MM/YY format


@dataclass
class Renter:
    first_name: str = ""
    last_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    telegram_chat_id: Optional[str] = None
    credit_cards: list[CreditCard] = field(default_factory=list)
    id: Optional[str] = None
    
    @classmethod
    def collection_name(cls) -> str:
        return "Renters"
