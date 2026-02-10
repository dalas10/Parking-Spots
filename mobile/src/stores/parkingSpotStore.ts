import { create } from 'zustand';
import { ParkingSpot, ParkingSpotListItem, ParkingSpotSearch } from '../types';
import { parkingSpotService } from '../services';

interface Location {
  latitude: number;
  longitude: number;
}

interface ParkingSpotState {
  // Search results
  searchResults: ParkingSpotListItem[];
  isSearching: boolean;
  searchError: string | null;
  
  // Current location
  currentLocation: Location | null;
  
  // Selected spot
  selectedSpot: ParkingSpot | null;
  isLoadingSpot: boolean;
  
  // Owner's spots
  mySpots: ParkingSpot[];
  isLoadingMySpots: boolean;
  
  // Search filters
  searchFilters: Partial<ParkingSpotSearch>;
  
  // Actions
  setCurrentLocation: (location: Location) => void;
  searchNearby: (params?: Partial<ParkingSpotSearch>) => Promise<void>;
  getSpotDetails: (id: string) => Promise<ParkingSpot>;
  fetchMySpots: () => Promise<void>;
  createSpot: (data: any) => Promise<ParkingSpot>;
  updateSpot: (id: string, data: any) => Promise<ParkingSpot>;
  deleteSpot: (id: string) => Promise<void>;
  toggleSpotAvailability: (id: string, isAvailable: boolean) => Promise<void>;
  setSearchFilters: (filters: Partial<ParkingSpotSearch>) => void;
  clearSearchResults: () => void;
}

export const useParkingSpotStore = create<ParkingSpotState>((set, get) => ({
  searchResults: [],
  isSearching: false,
  searchError: null,
  currentLocation: null,
  selectedSpot: null,
  isLoadingSpot: false,
  mySpots: [],
  isLoadingMySpots: false,
  searchFilters: {
    radius_km: 10,
  },

  setCurrentLocation: (location: Location) => {
    set({ currentLocation: location });
  },

  searchNearby: async (params?: Partial<ParkingSpotSearch>) => {
    const { currentLocation, searchFilters } = get();
    
    // Allow search without location if text search (q) or city is provided
    const hasTextSearch = params?.q || params?.city;
    if (!currentLocation && !params?.latitude && !hasTextSearch) {
      set({ searchError: 'Location or search text is required' });
      return;
    }
    
    set({ isSearching: true, searchError: null });
    
    try {
      const searchParams: Partial<ParkingSpotSearch> = {
        ...searchFilters,
        ...params,
      };
      
      // Add location only if available
      if (currentLocation && !params?.latitude) {
        searchParams.latitude = currentLocation.latitude;
        searchParams.longitude = currentLocation.longitude;
      }
      
      const results = await parkingSpotService.searchParkingSpots(searchParams as ParkingSpotSearch);
      set({ searchResults: results, isSearching: false });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Search failed';
      set({ searchError: message, isSearching: false });
    }
  },

  getSpotDetails: async (id: string) => {
    set({ isLoadingSpot: true });
    try {
      const spot = await parkingSpotService.getParkingSpotById(id);
      set({ selectedSpot: spot, isLoadingSpot: false });
      return spot;
    } catch (error) {
      set({ isLoadingSpot: false });
      throw error;
    }
  },

  fetchMySpots: async () => {
    set({ isLoadingMySpots: true });
    try {
      const spots = await parkingSpotService.getMyParkingSpots();
      set({ mySpots: spots, isLoadingMySpots: false });
    } catch (error) {
      set({ isLoadingMySpots: false });
      throw error;
    }
  },

  createSpot: async (data: any) => {
    const spot = await parkingSpotService.createParkingSpot(data);
    set((state) => ({ mySpots: [...state.mySpots, spot] }));
    return spot;
  },

  updateSpot: async (id: string, data: any) => {
    const spot = await parkingSpotService.updateParkingSpot(id, data);
    set((state) => ({
      mySpots: state.mySpots.map((s) => (s.id === id ? spot : s)),
      selectedSpot: state.selectedSpot?.id === id ? spot : state.selectedSpot,
    }));
    return spot;
  },

  deleteSpot: async (id: string) => {
    await parkingSpotService.deleteParkingSpot(id);
    set((state) => ({
      mySpots: state.mySpots.filter((s) => s.id !== id),
      selectedSpot: state.selectedSpot?.id === id ? null : state.selectedSpot,
    }));
  },

  toggleSpotAvailability: async (id: string, isAvailable: boolean) => {
    const spot = await parkingSpotService.toggleAvailability(id, isAvailable);
    set((state) => ({
      mySpots: state.mySpots.map((s) => (s.id === id ? spot : s)),
    }));
  },

  setSearchFilters: (filters: Partial<ParkingSpotSearch>) => {
    set((state) => ({
      searchFilters: { ...state.searchFilters, ...filters },
    }));
  },

  clearSearchResults: () => {
    set({ searchResults: [], searchError: null });
  },
}));
