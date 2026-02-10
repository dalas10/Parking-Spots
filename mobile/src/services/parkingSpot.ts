import apiClient from './api';
import {
  ParkingSpot,
  ParkingSpotListItem,
  ParkingSpotCreate,
  ParkingSpotSearch,
} from '../types';

export const parkingSpotService = {
  async searchParkingSpots(params: ParkingSpotSearch): Promise<ParkingSpotListItem[]> {
    const response = await apiClient.get<ParkingSpotListItem[]>('/parking-spots', params);
    return response.data;
  },

  async getParkingSpotById(id: string): Promise<ParkingSpot> {
    const response = await apiClient.get<ParkingSpot>(`/parking-spots/${id}`);
    return response.data;
  },

  async getMyParkingSpots(): Promise<ParkingSpot[]> {
    const response = await apiClient.get<ParkingSpot[]>('/parking-spots/my-spots');
    return response.data;
  },

  async createParkingSpot(data: ParkingSpotCreate): Promise<ParkingSpot> {
    const response = await apiClient.post<ParkingSpot>('/parking-spots', data);
    return response.data;
  },

  async updateParkingSpot(id: string, data: Partial<ParkingSpotCreate>): Promise<ParkingSpot> {
    const response = await apiClient.put<ParkingSpot>(`/parking-spots/${id}`, data);
    return response.data;
  },

  async deleteParkingSpot(id: string): Promise<void> {
    await apiClient.delete(`/parking-spots/${id}`);
  },

  async toggleAvailability(id: string, isAvailable: boolean): Promise<ParkingSpot> {
    const response = await apiClient.put<ParkingSpot>(`/parking-spots/${id}`, {
      is_available: isAvailable,
    });
    return response.data;
  },

  // Availability slots
  async addAvailabilitySlot(
    spotId: string,
    data: {
      day_of_week?: number;
      specific_date?: string;
      start_time: string;
      end_time: string;
      is_available?: boolean;
    }
  ): Promise<any> {
    const response = await apiClient.post(`/parking-spots/${spotId}/availability`, data);
    return response.data;
  },

  async getAvailabilitySlots(spotId: string): Promise<any[]> {
    const response = await apiClient.get<any[]>(`/parking-spots/${spotId}/availability`);
    return response.data;
  },

  async deleteAvailabilitySlot(spotId: string, slotId: string): Promise<void> {
    await apiClient.delete(`/parking-spots/${spotId}/availability/${slotId}`);
  },
};
