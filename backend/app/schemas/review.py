from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class ReviewBase(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5)
    cleanliness_rating: Optional[int] = Field(None, ge=1, le=5)
    accessibility_rating: Optional[int] = Field(None, ge=1, le=5)
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    value_rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    booking_id: UUID

class ReviewUpdate(BaseModel):
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    cleanliness_rating: Optional[int] = Field(None, ge=1, le=5)
    accessibility_rating: Optional[int] = Field(None, ge=1, le=5)
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    value_rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: UUID
    booking_id: UUID
    parking_spot_id: UUID
    reviewer_id: UUID
    owner_response: Optional[str] = None
    owner_responded_at: Optional[str] = None
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReviewWithUserResponse(ReviewResponse):
    reviewer_name: str
    reviewer_image: Optional[str] = None

class ReviewOwnerResponse(BaseModel):
    response: str

class ReviewHelpful(BaseModel):
    review_id: UUID

class ReviewSummary(BaseModel):
    average_rating: float
    total_reviews: int
    rating_breakdown: dict  # {5: count, 4: count, ...}
    average_cleanliness: Optional[float] = None
    average_accessibility: Optional[float] = None
    average_accuracy: Optional[float] = None
    average_value: Optional[float] = None
