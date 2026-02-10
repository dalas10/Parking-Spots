// Booking types
export type BookingStatus = 
  | 'pending'
  | 'confirmed'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'refunded';

export interface Booking {
  id: string;
  user_id: string;
  parking_spot_id: string;
  start_time: string;
  end_time: string;
  status: BookingStatus;
  total_amount: number;
  service_fee: number;
  owner_payout: number;
  payment_intent_id?: string;
  payment_status: string;
  vehicle_plate?: string;
  vehicle_make?: string;
  vehicle_model?: string;
  vehicle_color?: string;
  special_requests?: string;
  cancellation_reason?: string;
  checked_in_at?: string;
  checked_out_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BookingCreate {
  parking_spot_id: string;
  start_time: string;
  end_time: string;
  vehicle_plate?: string;
  vehicle_make?: string;
  vehicle_model?: string;
  vehicle_color?: string;
  special_requests?: string;
}

export interface BookingPriceCalculation {
  parking_spot_id: string;
  start_time: string;
  end_time: string;
}

export interface BookingPrice {
  subtotal: number;
  service_fee: number;
  total: number;
  owner_payout: number;
  duration_hours: number;
}
