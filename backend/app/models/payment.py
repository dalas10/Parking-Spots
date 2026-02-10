import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text
from app.db.types import GUID
import enum

from app.db.base import Base, TimestampMixin

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    booking_id = Column(GUID, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    
    # Stripe info
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    
    # Amount (in cents)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="usd")
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Refund info
    refund_amount = Column(Integer, default=0)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    payment_method = Column(String(50), nullable=True)  # card, apple_pay, etc.
    last_four = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.amount} cents>"


class Payout(Base, TimestampMixin):
    """Payouts to parking spot owners."""
    __tablename__ = "payouts"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    booking_id = Column(GUID, ForeignKey("bookings.id"), nullable=True)
    
    # Stripe info
    stripe_transfer_id = Column(String(255), nullable=True)
    stripe_payout_id = Column(String(255), nullable=True)
    
    # Amount
    amount = Column(Integer, nullable=False)  # in cents
    currency = Column(String(3), default="usd")
    
    # Status
    status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING)
    
    # Processing info
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Payout {self.id} - {self.amount} cents>"
