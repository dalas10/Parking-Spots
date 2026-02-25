from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.parking_spot import ParkingSpotType, VehicleSize

class ParkingSpotBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    spot_type: ParkingSpotType = ParkingSpotType.OUTDOOR
    vehicle_size: VehicleSize = VehicleSize.STANDARD
    
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    prefecture: str = Field(..., min_length=2, max_length=100)
    zip_code: str = Field(..., min_length=3, max_length=20)
    country: str = "Greece"
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    
    hourly_rate: int = Field(..., gt=0, description="Hourly rate in cents")
    daily_rate: Optional[int] = Field(None, gt=0, description="Daily rate in cents")
    monthly_rate: Optional[int] = Field(None, gt=0, description="Monthly rate in cents")
    
    is_covered: bool = False
    has_ev_charging: bool = False
    has_security: bool = False
    has_lighting: bool = False
    is_handicap_accessible: bool = False
    
    access_instructions: Optional[str] = None
    operating_hours: Optional[Dict[str, Any]] = None

class ParkingSpotCreate(ParkingSpotBase):
    images: List[str] = []

class ParkingSpotUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    spot_type: Optional[ParkingSpotType] = None
    vehicle_size: Optional[VehicleSize] = None
    hourly_rate: Optional[int] = None
    daily_rate: Optional[int] = None
    monthly_rate: Optional[int] = None
    is_covered: Optional[bool] = None
    has_ev_charging: Optional[bool] = None
    has_security: Optional[bool] = None
    has_lighting: Optional[bool] = None
    is_handicap_accessible: Optional[bool] = None
    access_instructions: Optional[str] = None
    operating_hours: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None

class ParkingSpotResponse(ParkingSpotBase):
    id: UUID
    owner_id: UUID
    images: List[str] = []
    is_active: bool
    is_available: bool
    total_bookings: int
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ParkingSpotListResponse(BaseModel):
    id: UUID
    title: str
    address: str
    city: str
    prefecture: str
    latitude: float
    longitude: float
    hourly_rate: int
    spot_type: ParkingSpotType
    is_available: bool
    average_rating: float
    total_reviews: int
    images: List[str] = []
    distance_km: Optional[float] = None
    
    class Config:
        from_attributes = True

# Availability Slot schemas
class AvailabilitySlotBase(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    specific_date: Optional[str] = None
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    is_available: bool = True

class AvailabilitySlotCreate(AvailabilitySlotBase):
    pass

class AvailabilitySlotResponse(AvailabilitySlotBase):
    id: UUID
    parking_spot_id: UUID
    
    class Config:
        from_attributes = True

# Search/Filter schemas
class ParkingSpotSearch(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    spot_type: Optional[ParkingSpotType] = None
    vehicle_size: Optional[VehicleSize] = None
    max_hourly_rate: Optional[int] = None
    has_ev_charging: Optional[bool] = None
    is_covered: Optional[bool] = None
    is_handicap_accessible: Optional[bool] = None
    sort_by: str = "distance"  # distance, price, rating
    page: int = 1
    page_size: int = 20
