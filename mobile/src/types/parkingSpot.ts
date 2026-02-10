// Parking spot types
export type ParkingSpotType = 'indoor' | 'outdoor' | 'covered' | 'garage' | 'driveway' | 'lot';
export type VehicleSize = 'motorcycle' | 'compact' | 'standard' | 'large' | 'oversized';

export interface ParkingSpot {
  id: string;
  owner_id: string;
  title: string;
  description?: string;
  spot_type: ParkingSpotType;
  vehicle_size: VehicleSize;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  latitude: number;
  longitude: number;
  hourly_rate: number;
  daily_rate?: number;
  monthly_rate?: number;
  is_covered: boolean;
  has_ev_charging: boolean;
  has_security: boolean;
  has_lighting: boolean;
  is_handicap_accessible: boolean;
  images: string[];
  is_active: boolean;
  is_available: boolean;
  operating_hours?: Record<string, { open: string; close: string }>;
  access_instructions?: string;
  total_bookings: number;
  average_rating: number;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

export interface ParkingSpotListItem {
  id: string;
  title: string;
  address: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
  hourly_rate: number;
  spot_type: ParkingSpotType;
  is_available: boolean;
  average_rating: number;
  total_reviews: number;
  images: string[];
  distance_km?: number;
}

export interface ParkingSpotCreate {
  title: string;
  description?: string;
  spot_type: ParkingSpotType;
  vehicle_size: VehicleSize;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country?: string;
  latitude: number;
  longitude: number;
  hourly_rate: number;
  daily_rate?: number;
  monthly_rate?: number;
  is_covered?: boolean;
  has_ev_charging?: boolean;
  has_security?: boolean;
  has_lighting?: boolean;
  is_handicap_accessible?: boolean;
  images?: string[];
  access_instructions?: string;
  operating_hours?: Record<string, { open: string; close: string }>;
}

export interface ParkingSpotSearch {
  latitude: number;
  longitude: number;
  radius_km?: number;
  spot_type?: ParkingSpotType;
  vehicle_size?: VehicleSize;
  max_hourly_rate?: number;
  has_ev_charging?: boolean;
  is_covered?: boolean;
  is_handicap_accessible?: boolean;
  page?: number;
  page_size?: number;
}
