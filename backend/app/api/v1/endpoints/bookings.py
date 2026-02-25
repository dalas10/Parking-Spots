from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.parking_spot import ParkingSpot
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import (
    BookingCreate, BookingUpdate, BookingResponse, 
    BookingStatusUpdate, BookingPriceCalculation, BookingPriceResponse
)
from app.api.deps import get_current_user
from app.core.config import settings
from app.cache import invalidate_spot_cache, invalidate_search_cache

router = APIRouter()

SERVICE_FEE_PERCENT = 0.10  # 10% service fee

def calculate_booking_price(hourly_rate: int, daily_rate: int | None, start: datetime, end: datetime) -> dict:
    """Calculate booking price based on duration."""
    duration = end - start
    hours = duration.total_seconds() / 3600
    
    # Use daily rate if booking is 8+ hours and daily rate exists
    if hours >= 8 and daily_rate:
        days = hours / 24
        subtotal = int(daily_rate * max(1, days))
    else:
        subtotal = int(hourly_rate * hours)
    
    service_fee = int(subtotal * SERVICE_FEE_PERCENT)
    total = subtotal + service_fee
    owner_payout = subtotal
    
    return {
        "subtotal": subtotal,
        "service_fee": service_fee,
        "total": total,
        "owner_payout": owner_payout,
        "duration_hours": round(hours, 2)
    }

@router.post("/calculate-price", response_model=BookingPriceResponse)
async def calculate_price(
    price_request: BookingPriceCalculation,
    db: AsyncSession = Depends(get_db)
):
    """Calculate booking price without creating a booking."""
    result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == price_request.parking_spot_id)
    )
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    if price_request.start_time >= price_request.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    return calculate_booking_price(
        spot.hourly_rate, 
        spot.daily_rate,
        price_request.start_time, 
        price_request.end_time
    )

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking."""
    # Get parking spot
    result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == booking_in.parking_spot_id)
    )
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    if not spot.is_available or not spot.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parking spot is not available"
        )
    
    if booking_in.start_time >= booking_in.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    if booking_in.start_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book in the past"
        )
    
    # Check for conflicting bookings with row-level lock to prevent race conditions
    # The with_for_update() ensures no other transaction can read/modify these rows
    # until this transaction commits, preventing double bookings
    result = await db.execute(
        select(Booking).where(
            and_(
                Booking.parking_spot_id == booking_in.parking_spot_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
                or_(
                    and_(
                        Booking.start_time <= booking_in.start_time,
                        Booking.end_time > booking_in.start_time
                    ),
                    and_(
                        Booking.start_time < booking_in.end_time,
                        Booking.end_time >= booking_in.end_time
                    ),
                    and_(
                        Booking.start_time >= booking_in.start_time,
                        Booking.end_time <= booking_in.end_time
                    )
                )
            )
        ).with_for_update()  # Lock rows to prevent race conditions
    )
    conflicting = result.scalars().first()
    
    if conflicting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot is already booked"
        )
    
    # Calculate price
    pricing = calculate_booking_price(
        spot.hourly_rate,
        spot.daily_rate,
        booking_in.start_time,
        booking_in.end_time
    )
    
    # Determine booking status based on payment configuration
    if settings.SKIP_PAYMENT_PROCESSING:
        # Auto-confirm for testing without payment
        booking_status = BookingStatus.CONFIRMED
        payment_status = "completed"
    else:
        # Require payment confirmation in production
        booking_status = BookingStatus.PENDING
        payment_status = "pending"
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        parking_spot_id=booking_in.parking_spot_id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        vehicle_plate=booking_in.vehicle_plate,
        vehicle_make=booking_in.vehicle_make,
        vehicle_model=booking_in.vehicle_model,
        vehicle_color=booking_in.vehicle_color,
        special_requests=booking_in.special_requests,
        total_amount=pricing["total"],
        service_fee=pricing["service_fee"],
        owner_payout=pricing["owner_payout"],
        status=booking_status,
        payment_status=payment_status
    )
    
    db.add(booking)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot is already booked"
        )
    await db.refresh(booking)
    
    # Reload with relationships so the response serializes correctly
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking.id)
        .options(selectinload(Booking.parking_spot))
    )
    booking = result.scalar_one()
    
    # Invalidate cache since booking affects availability
    await invalidate_spot_cache(str(booking_in.parking_spot_id))
    
    return booking

@router.get("/", response_model=List[BookingResponse])
async def list_my_bookings(
    status_filter: BookingStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List bookings for current user."""
    query = select(Booking).where(Booking.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Booking.status == status_filter)
    
    query = query.options(selectinload(Booking.parking_spot)).order_by(Booking.created_at.desc())
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return bookings

@router.get("/owner", response_model=List[BookingResponse])
async def list_owner_bookings(
    status_filter: BookingStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List bookings for spots owned by current user."""
    # Get owner's parking spots
    spots_result = await db.execute(
        select(ParkingSpot.id).where(ParkingSpot.owner_id == current_user.id)
    )
    spot_ids = [s[0] for s in spots_result.fetchall()]
    
    if not spot_ids:
        return []
    
    query = select(Booking).where(Booking.parking_spot_id.in_(spot_ids))
    
    if status_filter:
        query = query.where(Booking.status == status_filter)
    
    query = query.options(selectinload(Booking.parking_spot)).order_by(Booking.created_at.desc())
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get booking by ID."""
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.parking_spot))
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check authorization
    spot_result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == booking.parking_spot_id)
    )
    spot = spot_result.scalar_one_or_none()
    
    if booking.user_id != current_user.id and spot.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    return booking

@router.put("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    status_update: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update booking status (for owners/admins)."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Get parking spot for authorization
    spot_result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == booking.parking_spot_id)
    )
    spot = spot_result.scalar_one_or_none()
    
    # Authorization based on action
    if status_update.status == BookingStatus.CANCELLED:
        # Both user and owner can cancel
        if booking.user_id != current_user.id and spot.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        booking.cancellation_reason = status_update.cancellation_reason
    elif status_update.status == BookingStatus.CONFIRMED:
        # Only owner can confirm
        if spot.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can confirm bookings"
            )
    
    booking.status = status_update.status
    await db.flush()
    await db.refresh(booking)
    
    return booking

@router.post("/{booking_id}/check-in", response_model=BookingResponse)
async def check_in(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check in to a booking."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be confirmed before check-in"
        )
    
    booking.status = BookingStatus.IN_PROGRESS
    booking.checked_in_at = datetime.now(timezone.utc)
    
    await db.flush()
    await db.refresh(booking)
    
    return booking

@router.post("/{booking_id}/check-out", response_model=BookingResponse)
async def check_out(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check out from a booking."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if booking.status != BookingStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must be checked in before checking out"
        )
    
    booking.status = BookingStatus.COMPLETED
    booking.checked_out_at = datetime.now(timezone.utc)
    
    # Update parking spot stats
    spot_result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.id == booking.parking_spot_id)
    )
    spot = spot_result.scalar_one_or_none()
    if spot:
        spot.total_bookings += 1
    
    await db.flush()
    await db.refresh(booking)
    
    return booking
