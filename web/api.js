// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };
    
    // Add auth token if available
    if (isAuthenticated()) {
        defaultHeaders['Authorization'] = `Bearer ${getToken()}`;
    }
    
    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, config);
        
        // Handle 401 Unauthorized
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Parking Spots API
async function searchParkingSpots(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.q) queryParams.append('q', params.q);
    if (params.city) queryParams.append('city', params.city);
    if (params.spot_type) queryParams.append('spot_type', params.spot_type);
    if (params.has_ev_charging !== undefined) queryParams.append('has_ev_charging', params.has_ev_charging);
    if (params.is_covered !== undefined) queryParams.append('is_covered', params.is_covered);
    if (params.max_price) queryParams.append('max_price', params.max_price);
    if (params.start_time) queryParams.append('start_time', params.start_time);
    if (params.end_time) queryParams.append('end_time', params.end_time);
    if (params.limit) queryParams.append('limit', params.limit);
    
    return apiRequest(`/api/v1/parking-spots/?${queryParams.toString()}`);
}

async function getParkingSpot(spotId) {
    return apiRequest(`/api/v1/parking-spots/${spotId}`);
}

// Bookings API
async function createBooking(bookingData) {
    return apiRequest('/api/v1/bookings/', {
        method: 'POST',
        body: JSON.stringify(bookingData),
    });
}

async function getMyBookings(status = null) {
    const params = status ? `?status_filter=${status}` : '';
    return apiRequest(`/api/v1/bookings/${params}`);
}

async function getBooking(bookingId) {
    return apiRequest(`/api/v1/bookings/${bookingId}`);
}

async function cancelBooking(bookingId, reason = '') {
    return apiRequest(`/api/v1/bookings/${bookingId}/cancel`, {
        method: 'POST',
        body: JSON.stringify({ cancellation_reason: reason }),
    });
}

// Reviews API
async function getSpotReviews(spotId) {
    return apiRequest(`/api/v1/reviews/parking-spot/${spotId}`);
}

// User API
async function getUserProfile() {
    return apiRequest('/api/v1/users/me');
}

// Helper: Format currency
function formatCurrency(cents) {
    return `$${(cents / 100).toFixed(2)}`;
}

// Helper: Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Helper: Calculate duration
function calculateDuration(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const hours = Math.ceil((end - start) / (1000 * 60 * 60));
    return hours;
}

// Helper: Calculate booking cost
function calculateBookingCost(hourlyRate, hours) {
    const subtotal = hourlyRate * hours;
    const serviceFee = Math.ceil(subtotal * 0.10) + 50; // 10% + $0.50
    const total = subtotal + serviceFee;
    
    return { subtotal, serviceFee, total };
}
