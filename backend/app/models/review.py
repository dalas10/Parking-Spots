import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float
from app.db.types import GUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin

class Review(Base, TimestampMixin):
    __tablename__ = "reviews"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    booking_id = Column(GUID, ForeignKey("bookings.id"), nullable=False)
    parking_spot_id = Column(GUID, ForeignKey("parking_spots.id"), nullable=False)
    reviewer_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    
    # Rating (1-5 stars)
    overall_rating = Column(Integer, nullable=False)
    cleanliness_rating = Column(Integer, nullable=True)
    accessibility_rating = Column(Integer, nullable=True)
    accuracy_rating = Column(Integer, nullable=True)  # How accurate was the listing
    value_rating = Column(Integer, nullable=True)     # Value for money
    
    # Review content
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Owner response
    owner_response = Column(Text, nullable=True)
    owner_responded_at = Column(String(50), nullable=True)
    
    # Helpful votes
    helpful_count = Column(Integer, default=0)
    
    # Relationships
    booking = relationship("Booking", back_populates="review")
    parking_spot = relationship("ParkingSpot", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews_given", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<Review {self.id} - {self.overall_rating} stars>"
