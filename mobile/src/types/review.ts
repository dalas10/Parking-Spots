// Review types
export interface Review {
  id: string;
  booking_id: string;
  parking_spot_id: string;
  reviewer_id: string;
  overall_rating: number;
  cleanliness_rating?: number;
  accessibility_rating?: number;
  accuracy_rating?: number;
  value_rating?: number;
  title?: string;
  comment?: string;
  owner_response?: string;
  owner_responded_at?: string;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReviewWithUser extends Review {
  reviewer_name: string;
  reviewer_image?: string;
}

export interface ReviewCreate {
  booking_id: string;
  overall_rating: number;
  cleanliness_rating?: number;
  accessibility_rating?: number;
  accuracy_rating?: number;
  value_rating?: number;
  title?: string;
  comment?: string;
}

export interface ReviewSummary {
  average_rating: number;
  total_reviews: number;
  rating_breakdown: Record<number, number>;
  average_cleanliness?: number;
  average_accessibility?: number;
  average_accuracy?: number;
  average_value?: number;
}
