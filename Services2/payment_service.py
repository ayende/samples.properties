"""Payment processing service"""
from datetime import datetime
from models import Payment, DebtItem, PaymentMethod, PaymentAllocation


class PaymentService:
    """Service for processing payments and allocating to debt items"""
    
    @staticmethod
    def process_payment(session, payment: Payment):
        """Process a payment and allocate to debt items"""
        if not payment.Allocation:
            raise ValueError("Payment must have at least one allocation")
        
        # Store the payment
        session.store(payment)
        

        # Load all debt items
        debt_item_ids = [allocation.DebtItemId for allocation in payment.Allocation]
        debt_items = session.load(debt_item_ids, object_type=DebtItem) # Bulk load

        # Update debt items with payment allocations
        for allocation in payment.Allocation:
            if allocation.DebtItemId not in debt_items or debt_items[allocation.DebtItemId] is None:
                raise ValueError(f"Debt item {allocation.DebtItemId} not found")
            
            debt_item = debt_items[allocation.DebtItemId]
            debt_item.AmountPaid += allocation.AmountApplied
        
        session.save_changes()
    
    @staticmethod
    def create_payment_for_debts_with_card(
        session,
        renter_id: str,
        debt_item_ids: list,
        card: dict,
        payment_method: str
    ) -> float:
        """Create a payment for debts using a credit card"""
        
        # Load all debt items
        debt_items = session.load(debt_item_ids, object_type=DebtItem) # Bulk load
        
        total_amount = 0
        missing_debts = []
        
        for debt_id in debt_item_ids:
            if debt_id not in debt_items or debt_items[debt_id] is None:
                missing_debts.append(debt_id)
                continue
            
            debt = debt_items[debt_id]
            
            # Verify this debt belongs to the renter
            if renter_id not in debt.RenterIds:
                raise ValueError(f"Debt item {debt_id} does not belong to you")
            
            amount_due = debt.AmountDue - debt.AmountPaid
            total_amount += amount_due
        
        if missing_debts:
            raise ValueError(f"Debt items not found: {', '.join(missing_debts)}")
        
        # Create payment record
        allocations = []
        for debt_id in debt_item_ids:
            debt = debt_items[debt_id]
            amount_due = debt.AmountDue - debt.AmountPaid
            allocations.append(
                PaymentAllocation(
                    DebtItemId=debt_id,
                    AmountApplied=amount_due,
                    RenterId=renter_id
                )
            )
        
        payment = Payment(
            PaymentDate=datetime.now(),
            TotalAmountReceived=total_amount,
            PaymentMethods=[
                PaymentMethod(
                    Method=payment_method,
                    Amount=total_amount,
                    Details=f"{card.Type} ****{card.Last4Digits}"
                )
            ],
            Allocation=allocations
        )
        
        PaymentService.process_payment(session, payment)
        return total_amount
