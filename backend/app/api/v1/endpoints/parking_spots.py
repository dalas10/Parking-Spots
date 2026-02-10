from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from math import radians, cos, sin, asin, sqrt

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.parking_spot import ParkingSpot, AvailabilitySlot, ParkingSpotType, VehicleSize
from app.models.booking import Booking, BookingStatus
from app.schemas.parking_spot import (
    ParkingSpotCreate, ParkingSpotUpdate, ParkingSpotResponse,
    ParkingSpotListResponse, ParkingSpotSearch, AvailabilitySlotCreate,
    AvailabilitySlotResponse
)
from app.api.deps import get_current_user, get_current_owner

router = APIRouter()

def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance in kilometers between two points."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

@router.post("/", response_model=ParkingSpotResponse, status_code=status.HTTP_201_CREATED)
async def create_parking_spot(
    spot_in: ParkingSpotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new parking spot listing."""
    # Update user role to owner if they're a renter
    if current_user.role == UserRole.RENTER:
        current_user.role = UserRole.OWNER
    
    spot = ParkingSpot(
        owner_id=current_user.id,
        **spot_in.model_dump()
    )
    
    db.add(spot)
    await db.commit()
    await db.refresh(spot)
    
    return spot

@router.get("/search", response_model=List[ParkingSpotListResponse])
async def search_parking_spots(
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    spot_type: Optional[str] = None,
    vehicle_size: Optional[VehicleSize] = None,
    max_price: Optional[int] = Query(None, gt=0),
    has_ev_charging: Optional[bool] = None,
    is_covered: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(50.0, gt=0, le=500),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search parking spots with multiple filter options including time-based availability."""
    query = select(ParkingSpot).where(
        and_(
            ParkingSpot.is_active == True,
            ParkingSpot.is_available == True
        )
    )
    
    # Apply filters
    if city:
        query = query.where(func.lower(ParkingSpot.city).like(f"%{city.lower()}%"))
    if state:
        query = query.where(func.lower(ParkingSpot.state).like(f"%{state.lower()}%"))
    if zip_code:
        query = query.where(ParkingSpot.zip_code == zip_code)
    if spot_type:
        query = query.where(func.lower(ParkingSpot.spot_type) == spot_type.lower())
    if vehicle_size:
        query = query.where(ParkingSpot.vehicle_size == vehicle_size)
    if max_price:
        query = query.where(ParkingSpot.hourly_rate <= max_price)
    if has_ev_charging is not None:
        query = query.where(ParkingSpot.has_ev_charging == has_ev_charging)
    if is_covered is not None:
        query = query.where(ParkingSpot.is_covered == is_covered)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    spots = result.scalars().all()
    
    # Filter out spots with conflicting bookings if time range is provided
    if start_time and end_time:
        available_spots = []
        for spot in spots:
            # Check for conflicting bookings
            conflict_query = select(Booking).where(
                and_(
                    Booking.parking_spot_id == spot.id,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
                    or_(
                        and_(
                            Booking.start_time <= start_time,
                            Booking.end_time > start_time
                        ),
                        and_(
                            Booking.start_time < end_time,
                            Booking.end_time >= end_time
                        ),
                        and_(
                            Booking.start_time >= start_time,
                            Booking.end_time <= end_time
                        )
                    )
                )
            )
            conflict_result = await db.execute(conflict_query)
            has_conflict = conflict_result.scalar_one_or_none()
            
            if not has_conflict:
                available_spots.append(spot)
        
        spots = available_spots
    
    # Build response with distance calculation if location provided
    response_spots = []
    for spot in spots:
        spot_dict = {
            "id": str(spot.id),
            "title": spot.title,
            "address": spot.address,
            "city": spot.city,
            "state": spot.state,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "hourly_rate": spot.hourly_rate,
            "daily_rate": spot.daily_rate,
            "monthly_rate": spot.monthly_rate,
            "spot_type": spot.spot_type,
            "vehicle_size": spot.vehicle_size,
            "is_covered": spot.is_covered,
            "has_ev_charging": spot.has_ev_charging,
            "has_security": spot.has_security,
            "has_lighting": spot.has_lighting,
            "is_handicap_accessible": spot.is_handicap_accessible,
            "is_available": spot.is_available,
            "average_rating": spot.average_rating,
            "total_reviews": spot.total_reviews,
            "images": spot.images or [],
            "distance_km": None
        }
        
        if latitude and longitude:
            distance = haversine(longitude, latitude, spot.longitude, spot.latitude)
            if distance <= radius_km:
                spot_dict["distance_km"] = round(distance, 2)
                response_spots.append(spot_dict)
        else:
            response_spots.append(spot_dict)
    
    # Sort by distance if location provided
    if latitude and longitude:
        response_spots.sort(key=lambda x: x["distance_km"] if x["distance_km"] is not None else float('inf'))
    
    return response_spots

@router.get("/", response_model=List[ParkingSpotListResponse])
async def list_parking_spots(
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, le=100),
    spot_type: Optional[ParkingSpotType] = None,
    vehicle_size: Optional[VehicleSize] = None,
    max_hourly_rate: Optional[int] = Query(None, gt=0),
    has_ev_charging: Optional[bool] = None,
    is_covered: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List parking spots with optional filters and location-based search."""
    query = select(ParkingSpot).where(
        and_(
            ParkingSpot.is_active == True,
            ParkingSpot.is_available == True
        )
    )
    
    # Apply filters
    if spot_type:
        query = query.where(ParkingSpot.spot_type == spot_type)
    if vehicle_size:
        query = query.where(ParkingSpot.vehicle_size == vehicle_size)
    if max_hourly_rate:
        query = query.where(ParkingSpot.hourly_rate <= max_hourly_rate)
    if has_ev_charging is not None:
        query = query.where(ParkingSpot.has_ev_charging == has_ev_charging)
    if is_covered is not None:
        query = query.where(ParkingSpot.is_covered == is_covered)
    
    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    spots = result.scalars().all()
    
    # Calculate distance if location provided
    response_spots = []
    for spot in spots:
        spot_dict = {
            "id": spot.id,
            "title": spot.title,
            "address": spot.address,
            "city": spot.city,
            "state": spot.state,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "hourly_rate": spot.hourly_rate,
            "spot_type": spot.spot_type,
            "is_available": spot.is_available,
            "average_rating": spot.average_rating,
            "total_reviews": spot.total_reviews,
            "images": spot.images or [],
            "distance_km": None
        }
        
        if latitude and longitude:
            distance = haversine(longitude, latitude, spot.longitude, spot.latitude)
            if distance <= radius_km:
                spot_dict["distance_km"] = round(distance, 2)
                response_spots.append(spot_dict)
        else:
            response_spots.append(spot_dict)
    
    # Sort by distance if location provided
    if latitude and longitude:
        response_spots.sort(key=lambda x: x["distance_km"] or float('inf'))
    
    return response_spots

@router.get("/my-spots", response_model=List[ParkingSpotResponse])
async def get_my_parking_spots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get parking spots owned by current user."""
    result = await db.execute(
        select(ParkingSpot).where(ParkingSpot.owner_id == current_user.id)
    )
    spots = result.scalars().all()
    return spots

@router.get("/{spot_id}", response_model=ParkingSpotResponse)
async def get_parking_spot(spot_id: str, db: AsyncSession = Depends(get_db)):
    """Get parking spot by ID."""
    result = await db.execute(select(ParkingSpot).where(ParkingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    return spot

@router.put("/{spot_id}", response_model=ParkingSpotResponse)
async def update_parking_spot(
    spot_id: str,
    spot_update: ParkingSpotUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a parking spot."""
    result = await db.execute(select(ParkingSpot).where(ParkingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    if spot.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this parking spot"
        )
    
    update_data = spot_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spot, field, value)
    
    await db.commit()
    await db.refresh(spot)
    
    return spot

@router.delete("/{spot_id}")
async def delete_parking_spot(
    spot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a parking spot."""
    result = await db.execute(select(ParkingSpot).where(ParkingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    if spot.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this parking spot"
        )
    
    await db.delete(spot)
    await db.commit()
    
    return {"message": "Parking spot deleted successfully"}

# Availability Slot endpoints
@router.post("/{spot_id}/availability", response_model=AvailabilitySlotResponse)
async def add_availability_slot(
    spot_id: str,
    slot_in: AvailabilitySlotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add availability slot to a parking spot."""
    result = await db.execute(select(ParkingSpot).where(ParkingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    if spot.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this parking spot"
        )
    
    slot = AvailabilitySlot(
        parking_spot_id=spot.id,
        **slot_in.model_dump()
    )
    
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    
    return slot

@router.get("/{spot_id}/availability", response_model=List[AvailabilitySlotResponse])
async def get_availability_slots(spot_id: str, db: AsyncSession = Depends(get_db)):
    """Get availability slots for a parking spot."""
    result = await db.execute(
        select(AvailabilitySlot).where(AvailabilitySlot.parking_spot_id == spot_id)
    )
    slots = result.scalars().all()
    return slots

@router.delete("/{spot_id}/availability/{slot_id}")
async def delete_availability_slot(
    spot_id: str,
    slot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an availability slot."""
    result = await db.execute(select(ParkingSpot).where(ParkingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot or spot.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    result = await db.execute(
        select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.id == slot_id,
                AvailabilitySlot.parking_spot_id == spot_id
            )
        )
    )
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability slot not found"
        )
    
    await db.delete(slot)
    await db.commit()
    
    return {"message": "Availability slot deleted"}
