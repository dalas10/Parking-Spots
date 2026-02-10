import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text
from app.db.types import GUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    parking_spot_id = Column(GUID, ForeignKey("parking_spots.id"), nullable=False)
    
    # Booking times
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    
    # Pricing
    total_amount = Column(Integer, nullable=False)  # in cents
    service_fee = Column(Integer, default=0)        # in cents
    owner_payout = Column(Integer, default=0)       # in cents
    
    # Payment
    payment_intent_id = Column(String(255), nullable=True)
    payment_status = Column(String(50), default="pending")
    
    # Vehicle info
    vehicle_plate = Column(String(20), nullable=True)
    vehicle_make = Column(String(50), nullable=True)
    vehicle_model = Column(String(50), nullable=True)
    vehicle_color = Column(String(30), nullable=True)
    
    # Notes
    special_requests = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Check-in/out timestamps
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    checked_out_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    parking_spot = relationship("ParkingSpot", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)
    
    def __repr__(self):
        return f"<Booking {self.id}>"
