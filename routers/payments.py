"""API router for payments"""
from fastapi import APIRouter, HTTPException
from database import get_session
from models import Payment
from services.payment_service import PaymentService

router = APIRouter()


@router.post("")
async def create(payment: Payment):
    """Process a payment"""
    async with get_session() as session:
        try:
            PaymentService.process_payment(session, payment)
            return payment
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
