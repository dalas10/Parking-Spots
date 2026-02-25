from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.booking import BookingStatus

class ParkingSpotInBooking(BaseModel):
    """Minimal parking spot info for booking display"""
    id: UUID
    title: str
    address: str
    city: str
    prefecture: str
    
    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    parking_spot_id: UUID
    start_time: datetime
    end_time: datetime
    vehicle_plate: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    special_requests: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    vehicle_plate: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    special_requests: Optional[str] = None

class BookingResponse(BookingBase):
    id: UUID
    user_id: UUID
    status: BookingStatus
    total_amount: int
    service_fee: int
    owner_payout: int
    payment_intent_id: Optional[str] = None
    payment_status: str
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    parking_spot: Optional[ParkingSpotInBooking] = None
    
    class Config:
        from_attributes = True

class BookingDetailResponse(BookingResponse):
    parking_spot_title: str
    parking_spot_address: str
    parking_spot_latitude: float
    parking_spot_longitude: float
    owner_name: str
    owner_phone: Optional[str] = None
    access_instructions: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    cancellation_reason: Optional[str] = None

class CheckInOut(BaseModel):
    booking_id: UUID

class BookingPriceCalculation(BaseModel):
    parking_spot_id: UUID
    start_time: datetime
    end_time: datetime

class BookingPriceResponse(BaseModel):
    subtotal: int
    service_fee: int
    total: int
    owner_payout: int
    duration_hours: float
