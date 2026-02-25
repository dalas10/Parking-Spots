import uuid
from sqlalchemy import Column, String, Boolean, Float, Integer, Text, ForeignKey, Enum, JSON
from app.db.types import GUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin

class ParkingSpotType(str, enum.Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    COVERED = "covered"
    GARAGE = "garage"
    DRIVEWAY = "driveway"
    LOT = "lot"

class VehicleSize(str, enum.Enum):
    MOTORCYCLE = "motorcycle"
    COMPACT = "compact"
    STANDARD = "standard"
    LARGE = "large"
    OVERSIZED = "oversized"

class ParkingSpot(Base, TimestampMixin):
    __tablename__ = "parking_spots"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    spot_type = Column(Enum(ParkingSpotType), default=ParkingSpotType.OUTDOOR)
    vehicle_size = Column(Enum(VehicleSize), default=VehicleSize.STANDARD)
    
    # Location
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    prefecture = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), default="Greece")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Pricing (in cents to avoid floating point issues)
    hourly_rate = Column(Integer, nullable=False)  # in cents
    daily_rate = Column(Integer, nullable=True)    # in cents
    monthly_rate = Column(Integer, nullable=True)  # in cents
    
    # Features
    is_covered = Column(Boolean, default=False)
    has_ev_charging = Column(Boolean, default=False)
    has_security = Column(Boolean, default=False)
    has_lighting = Column(Boolean, default=False)
    is_handicap_accessible = Column(Boolean, default=False)
    
    # Images
    images = Column(JSON, default=[])
    
    # Availability
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    
    # Operating hours (stored as JSON)
    # Example: {"monday": {"open": "08:00", "close": "22:00"}, ...}
    operating_hours = Column(JSON, nullable=True)
    
    # Access instructions
    access_instructions = Column(Text, nullable=True)
    
    # Stats
    total_bookings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Relationships
    owner = relationship("User", back_populates="parking_spots")
    bookings = relationship("Booking", back_populates="parking_spot", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="parking_spot", cascade="all, delete-orphan")
    availability_slots = relationship("AvailabilitySlot", back_populates="parking_spot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ParkingSpot {self.title}>"


class AvailabilitySlot(Base, TimestampMixin):
    """Represents available time slots for a parking spot."""
    __tablename__ = "availability_slots"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    parking_spot_id = Column(GUID, ForeignKey("parking_spots.id"), nullable=False)
    
    # Day of week (0=Monday, 6=Sunday) or specific date
    day_of_week = Column(Integer, nullable=True)  # For recurring availability
    specific_date = Column(String(10), nullable=True)  # For specific date (YYYY-MM-DD)
    
    start_time = Column(String(5), nullable=False)  # HH:MM format
    end_time = Column(String(5), nullable=False)    # HH:MM format
    
    is_available = Column(Boolean, default=True)
    
    # Relationships
    parking_spot = relationship("ParkingSpot", back_populates="availability_slots")
