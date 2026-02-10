import { create } from 'zustand';
import { Booking, BookingStatus, BookingPrice } from '../types';
import { bookingService } from '../services';

interface BookingState {
  // My bookings (as renter)
  myBookings: Booking[];
  isLoadingMyBookings: boolean;
  
  // Owner bookings (bookings on my spots)
  ownerBookings: Booking[];
  isLoadingOwnerBookings: boolean;
  
  // Current booking
  currentBooking: Booking | null;
  
  // Price calculation
  calculatedPrice: BookingPrice | null;
  isCalculatingPrice: boolean;
  
  // Actions
  fetchMyBookings: (status?: BookingStatus) => Promise<void>;
  fetchOwnerBookings: (status?: BookingStatus) => Promise<void>;
  getBookingDetails: (id: string) => Promise<Booking>;
  calculatePrice: (spotId: string, startTime: string, endTime: string) => Promise<BookingPrice>;
  createBooking: (data: any) => Promise<Booking>;
  confirmBooking: (id: string) => Promise<void>;
  cancelBooking: (id: string, reason?: string) => Promise<void>;
  checkIn: (id: string) => Promise<void>;
  checkOut: (id: string) => Promise<void>;
  clearCurrentBooking: () => void;
}

export const useBookingStore = create<BookingState>((set, get) => ({
  myBookings: [],
  isLoadingMyBookings: false,
  ownerBookings: [],
  isLoadingOwnerBookings: false,
  currentBooking: null,
  calculatedPrice: null,
  isCalculatingPrice: false,

  fetchMyBookings: async (status?: BookingStatus) => {
    set({ isLoadingMyBookings: true });
    try {
      const bookings = await bookingService.getMyBookings(status);
      set({ myBookings: bookings, isLoadingMyBookings: false });
    } catch (error) {
      set({ isLoadingMyBookings: false });
      throw error;
    }
  },

  fetchOwnerBookings: async (status?: BookingStatus) => {
    set({ isLoadingOwnerBookings: true });
    try {
      const bookings = await bookingService.getOwnerBookings(status);
      set({ ownerBookings: bookings, isLoadingOwnerBookings: false });
    } catch (error) {
      set({ isLoadingOwnerBookings: false });
      throw error;
    }
  },

  getBookingDetails: async (id: string) => {
    const booking = await bookingService.getBookingById(id);
    set({ currentBooking: booking });
    return booking;
  },

  calculatePrice: async (spotId: string, startTime: string, endTime: string) => {
    set({ isCalculatingPrice: true });
    try {
      const price = await bookingService.calculatePrice({
        parking_spot_id: spotId,
        start_time: startTime,
        end_time: endTime,
      });
      set({ calculatedPrice: price, isCalculatingPrice: false });
      return price;
    } catch (error) {
      set({ isCalculatingPrice: false });
      throw error;
    }
  },

  createBooking: async (data: any) => {
    const booking = await bookingService.createBooking(data);
    set((state) => ({
      myBookings: [booking, ...state.myBookings],
      currentBooking: booking,
    }));
    return booking;
  },

  confirmBooking: async (id: string) => {
    const booking = await bookingService.confirmBooking(id);
    set((state) => ({
      ownerBookings: state.ownerBookings.map((b) => (b.id === id ? booking : b)),
      currentBooking: state.currentBooking?.id === id ? booking : state.currentBooking,
    }));
  },

  cancelBooking: async (id: string, reason?: string) => {
    const booking = await bookingService.cancelBooking(id, reason);
    set((state) => ({
      myBookings: state.myBookings.map((b) => (b.id === id ? booking : b)),
      ownerBookings: state.ownerBookings.map((b) => (b.id === id ? booking : b)),
      currentBooking: state.currentBooking?.id === id ? booking : state.currentBooking,
    }));
  },

  checkIn: async (id: string) => {
    const booking = await bookingService.checkIn(id);
    set((state) => ({
      myBookings: state.myBookings.map((b) => (b.id === id ? booking : b)),
      currentBooking: state.currentBooking?.id === id ? booking : state.currentBooking,
    }));
  },

  checkOut: async (id: string) => {
    const booking = await bookingService.checkOut(id);
    set((state) => ({
      myBookings: state.myBookings.map((b) => (b.id === id ? booking : b)),
      currentBooking: state.currentBooking?.id === id ? booking : state.currentBooking,
    }));
  },

  clearCurrentBooking: () => {
    set({ currentBooking: null, calculatedPrice: null });
  },
}));
