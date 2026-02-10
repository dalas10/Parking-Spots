from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from app.models.payment import PaymentStatus, PayoutStatus

class PaymentIntentCreate(BaseModel):
    booking_id: UUID

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str

class PaymentConfirm(BaseModel):
    payment_intent_id: str

class PaymentResponse(BaseModel):
    id: UUID
    booking_id: UUID
    amount: int
    currency: str
    status: PaymentStatus
    payment_method: Optional[str] = None
    last_four: Optional[str] = None
    card_brand: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class RefundRequest(BaseModel):
    payment_id: UUID
    amount: Optional[int] = None  # Partial refund amount, None for full refund
    reason: Optional[str] = None

class RefundResponse(BaseModel):
    id: UUID
    original_amount: int
    refund_amount: int
    status: PaymentStatus
    refunded_at: datetime

class PayoutResponse(BaseModel):
    id: UUID
    owner_id: UUID
    booking_id: Optional[UUID] = None
    amount: int
    currency: str
    status: PayoutStatus
    processed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PayoutSummary(BaseModel):
    total_earnings: int
    pending_payouts: int
    completed_payouts: int
    this_month_earnings: int

class ConnectAccountCreate(BaseModel):
    """For Stripe Connect onboarding."""
    country: str = "US"
    business_type: str = "individual"

class ConnectAccountResponse(BaseModel):
    account_id: str
    onboarding_url: str
