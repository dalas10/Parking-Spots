import apiClient from './api';
import { Review, ReviewWithUser, ReviewCreate, ReviewSummary } from '../types';

export const reviewService = {
  async createReview(data: ReviewCreate): Promise<Review> {
    const response = await apiClient.post<Review>('/reviews', data);
    return response.data;
  },

  async getSpotReviews(
    spotId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<ReviewWithUser[]> {
    const response = await apiClient.get<ReviewWithUser[]>(`/reviews/spot/${spotId}`, {
      page,
      page_size: pageSize,
    });
    return response.data;
  },

  async getReviewSummary(spotId: string): Promise<ReviewSummary> {
    const response = await apiClient.get<ReviewSummary>(`/reviews/spot/${spotId}/summary`);
    return response.data;
  },

  async getReviewById(id: string): Promise<Review> {
    const response = await apiClient.get<Review>(`/reviews/${id}`);
    return response.data;
  },

  async updateReview(id: string, data: Partial<ReviewCreate>): Promise<Review> {
    const response = await apiClient.put<Review>(`/reviews/${id}`, data);
    return response.data;
  },

  async addOwnerResponse(reviewId: string, response: string): Promise<Review> {
    const res = await apiClient.post<Review>(`/reviews/${reviewId}/response`, {
      response,
    });
    return res.data;
  },

  async markHelpful(reviewId: string): Promise<{ message: string; helpful_count: number }> {
    const response = await apiClient.post<{ message: string; helpful_count: number }>(
      `/reviews/${reviewId}/helpful`
    );
    return response.data;
  },

  async deleteReview(id: string): Promise<void> {
    await apiClient.delete(`/reviews/${id}`);
  },
};
