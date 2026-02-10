import uuid
from sqlalchemy import Column, String, Boolean, Enum, Float
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin
from app.db.types import GUID

class UserRole(str, enum.Enum):
    OWNER = "owner"
    RENTER = "renter"
    ADMIN = "admin"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    profile_image = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.RENTER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'facebook', etc.
    oauth_id = Column(String(255), nullable=True, index=True)  # ID from OAuth provider
    
    # Stripe customer ID for payments
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Location (for finding nearby parking)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Relationships
    parking_spots = relationship("ParkingSpot", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    
    def __repr__(self):
        return f"<User {self.email}>"
