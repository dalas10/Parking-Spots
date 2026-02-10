import apiClient from './api';
import {
  Booking,
  BookingCreate,
  BookingPrice,
  BookingPriceCalculation,
  BookingStatus,
} from '../types';

export const bookingService = {
  async calculatePrice(data: BookingPriceCalculation): Promise<BookingPrice> {
    const response = await apiClient.post<BookingPrice>('/bookings/calculate-price', data);
    return response.data;
  },

  async createBooking(data: BookingCreate): Promise<Booking> {
    const response = await apiClient.post<Booking>('/bookings', data);
    return response.data;
  },

  async getMyBookings(status?: BookingStatus): Promise<Booking[]> {
    const params = status ? { status_filter: status } : undefined;
    const response = await apiClient.get<Booking[]>('/bookings', params);
    return response.data;
  },

  async getOwnerBookings(status?: BookingStatus): Promise<Booking[]> {
    const params = status ? { status_filter: status } : undefined;
    const response = await apiClient.get<Booking[]>('/bookings/owner', params);
    return response.data;
  },

  async getBookingById(id: string): Promise<Booking> {
    const response = await apiClient.get<Booking>(`/bookings/${id}`);
    return response.data;
  },

  async updateBookingStatus(
    id: string,
    status: BookingStatus,
    cancellationReason?: string
  ): Promise<Booking> {
    const response = await apiClient.put<Booking>(`/bookings/${id}/status`, {
      status,
      cancellation_reason: cancellationReason,
    });
    return response.data;
  },

  async confirmBooking(id: string): Promise<Booking> {
    return this.updateBookingStatus(id, 'confirmed');
  },

  async cancelBooking(id: string, reason?: string): Promise<Booking> {
    return this.updateBookingStatus(id, 'cancelled', reason);
  },

  async checkIn(id: string): Promise<Booking> {
    const response = await apiClient.post<Booking>(`/bookings/${id}/check-in`);
    return response.data;
  },

  async checkOut(id: string): Promise<Booking> {
    const response = await apiClient.post<Booking>(`/bookings/${id}/check-out`);
    return response.data;
  },
};
