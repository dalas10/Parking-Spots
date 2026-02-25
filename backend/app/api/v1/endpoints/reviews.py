from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.parking_spot import ParkingSpot
from app.models.booking import Booking, BookingStatus
from app.models.review import Review
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewWithUserResponse,
    ReviewOwnerResponse, ReviewSummary
)
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a review for a completed booking."""
    # Get the booking
    result = await db.execute(select(Booking).where(Booking.id == review_in.booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own bookings"
        )
    
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review completed bookings"
        )
    
    # Check if already reviewed
    existing_result = await db.execute(
        select(Review).where(Review.booking_id == review_in.booking_id)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking already has a review"
        )
    
    # Create review
    review = Review(
        booking_id=booking.id,
        parking_spot_id=booking.parking_spot_id,
        reviewer_id=current_user.id,
        overall_rating=review_in.overall_rating,
        cleanliness_rating=review_in.cleanliness_rating,
        accessibility_rating=review_in.accessibility_rating,
        accuracy_rating=review_in.accuracy_rating,
        value_rating=review_in.value_rating,
        title=review_in.title,
        comment=review_in.comment
    )
    
    db.add(review)
    
    # Update parking spot average rating
    spot_result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == booking.parking_spot_id)
    )
    spot = spot_result.scalar_one_or_none()
    
    if spot:
        # Calculate new average
        reviews_result = await db.execute(
            select(func.avg(Review.overall_rating), func.count(Review.id))
            .where(Review.parking_spot_id == spot.id)
        )
        avg_rating, count = reviews_result.one()
        
        # Include the new review in calculation
        new_count = (count or 0) + 1
        new_avg = ((avg_rating or 0) * (count or 0) + review_in.overall_rating) / new_count
        
        spot.average_rating = round(new_avg, 2)
        spot.total_reviews = new_count
    
    await db.flush()
    await db.refresh(review)
    
    return review

@router.get("/spot/{spot_id}", response_model=List[ReviewWithUserResponse])
async def get_spot_reviews(
    spot_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a parking spot."""
    offset = (page - 1) * page_size
    
    result = await db.execute(
        select(Review, User)
        .join(User, Review.reviewer_id == User.id)
        .where(Review.parking_spot_id == spot_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    reviews = []
    for review, user in result.fetchall():
        review_dict = {
            "id": review.id,
            "booking_id": review.booking_id,
            "parking_spot_id": review.parking_spot_id,
            "reviewer_id": review.reviewer_id,
            "overall_rating": review.overall_rating,
            "cleanliness_rating": review.cleanliness_rating,
            "accessibility_rating": review.accessibility_rating,
            "accuracy_rating": review.accuracy_rating,
            "value_rating": review.value_rating,
            "title": review.title,
            "comment": review.comment,
            "owner_response": review.owner_response,
            "owner_responded_at": review.owner_responded_at,
            "helpful_count": review.helpful_count,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "reviewer_name": user.full_name,
            "reviewer_image": user.profile_image
        }
        reviews.append(review_dict)
    
    return reviews

@router.get("/spot/{spot_id}/summary", response_model=ReviewSummary)
async def get_review_summary(spot_id: str, db: AsyncSession = Depends(get_db)):
    """Get review summary for a parking spot."""
    # Get overall stats
    stats_result = await db.execute(
        select(
            func.avg(Review.overall_rating),
            func.count(Review.id),
            func.avg(Review.cleanliness_rating),
            func.avg(Review.accessibility_rating),
            func.avg(Review.accuracy_rating),
            func.avg(Review.value_rating)
        ).where(Review.parking_spot_id == spot_id)
    )
    avg_rating, total, avg_clean, avg_access, avg_acc, avg_val = stats_result.one()
    
    # Get rating breakdown
    breakdown_result = await db.execute(
        select(Review.overall_rating, func.count(Review.id))
        .where(Review.parking_spot_id == spot_id)
        .group_by(Review.overall_rating)
    )
    
    rating_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating, count in breakdown_result.fetchall():
        rating_breakdown[rating] = count
    
    return {
        "average_rating": round(avg_rating, 2) if avg_rating else 0,
        "total_reviews": total or 0,
        "rating_breakdown": rating_breakdown,
        "average_cleanliness": round(avg_clean, 2) if avg_clean else None,
        "average_accessibility": round(avg_access, 2) if avg_access else None,
        "average_accuracy": round(avg_acc, 2) if avg_acc else None,
        "average_value": round(avg_val, 2) if avg_val else None
    }

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, db: AsyncSession = Depends(get_db)):
    """Get review by ID."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a review."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )
    
    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    await db.flush()
    await db.refresh(review)
    
    return review

@router.post("/{review_id}/response", response_model=ReviewResponse)
async def add_owner_response(
    review_id: str,
    response_data: ReviewOwnerResponse,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add owner response to a review."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if current user owns the parking spot
    spot_result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == review.parking_spot_id)
    )
    spot = spot_result.scalar_one_or_none()
    
    if not spot or spot.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can respond to reviews"
        )
    
    from datetime import datetime
    review.owner_response = response_data.response
    review.owner_responded_at = datetime.utcnow().isoformat()
    
    await db.flush()
    await db.refresh(review)
    
    return review

@router.post("/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a review as helpful."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.helpful_count += 1
    
    return {"message": "Review marked as helpful", "helpful_count": review.helpful_count}

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a review."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.reviewer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    await db.delete(review)
    
    return {"message": "Review deleted successfully"}
