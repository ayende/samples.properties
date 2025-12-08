"""Payment processing service"""
from decimal import Decimal
from models import Payment, DebtItem


class PaymentService:
    """Service for processing payments and allocating to debt items"""
    
    @staticmethod
    async def process_payment(session, payment: Payment):
        """Process a payment and allocate to debt items"""
        if not payment.allocation:
            raise ValueError("Payment must have at least one allocation")
        
        # Verify all debt items exist and update them
        for allocation in payment.allocation:
            debt_item = session.load(allocation.debt_item_id, object_type=DebtItem)
            if not debt_item:
                raise ValueError(f"Debt item not found: {allocation.debt_item_id}")
            
            # Update debt item
            debt_item.amount_paid += allocation.amount_applied
        
        # Store the payment
        session.store(payment)
        session.save_changes()
