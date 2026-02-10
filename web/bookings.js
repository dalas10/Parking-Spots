// Bookings page
let allBookings = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    
    loadBookings();
});

async function loadBookings(status = null) {
    const loadingBookings = document.getElementById('loadingBookings');
    const bookingsList = document.getElementById('bookingsList');
    const noBookings = document.getElementById('noBookings');
    
    loadingBookings.style.display = 'flex';
    bookingsList.innerHTML = '';
    noBookings.style.display = 'none';
    
    try {
        const bookings = await getMyBookings(status);
        allBookings = bookings;
        
        loadingBookings.style.display = 'none';
        
        if (bookings.length === 0) {
            noBookings.style.display = 'block';
            return;
        }
        
        // Group bookings by status
        const upcoming = bookings.filter(b => b.status === 'confirmed');
        const active = bookings.filter(b => b.status === 'in_progress');
        const completed = bookings.filter(b => b.status === 'completed');
        const cancelled = bookings.filter(b => b.status === 'cancelled');
        
        // Display bookings
        bookings.forEach(booking => {
            const card = createBookingCard(booking);
            bookingsList.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading bookings:', error);
        loadingBookings.style.display = 'none';
        noBookings.style.display = 'block';
        const errorText = window.t ? t('bookings.error_loading') : 'Error loading bookings:';
        noBookings.innerHTML = `<p>${errorText} ${error.message}</p>`;
    }
}

function createBookingCard(booking) {
    const card = document.createElement('div');
    card.className = 'booking-card';
    
    const statusClass = `status-${booking.status}`;
    const statusText = booking.status.replace('_', ' ').toUpperCase();
    
    card.innerHTML = `
        <div class="booking-icon">🅿️</div>
        <div class="booking-details">
            <h3>${booking.parking_spot?.title || 'Parking Spot'}</h3>
            <div class="booking-meta">
                📍 ${booking.parking_spot?.city || 'N/A'}, ${booking.parking_spot?.state || ''}
            </div>
            <div class="booking-meta">
                📅 ${formatDate(booking.start_time)} - ${formatDate(booking.end_time)}
            </div>
            <div class="booking-meta">
                🚗 ${booking.vehicle_make} ${booking.vehicle_model} (${booking.vehicle_plate})
            </div>
            <div class="booking-meta">
                💰 Total: ${formatCurrency(booking.total_amount)}
            </div>
            <span class="booking-status ${statusClass}">${statusText}</span>
        </div>
        <div class="booking-actions">
            <button class="btn-secondary btn-small" onclick="viewBooking('${booking.id}')">
                ${window.t ? t('bookings.view_details') : 'View Details'}
            </button>
            ${booking.status === 'confirmed' ? `
                <button class="btn-danger btn-small" onclick="cancelBookingConfirm('${booking.id}')">
                    ${window.t ? t('bookings.cancel') : 'Cancel'}
                </button>
            ` : ''}
        </div>
    `;
    
    return card;
}

function filterBookings(status) {
    currentFilter = status;
    
    // Update active tab
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter bookings
    const filtered = status === 'all' 
        ? allBookings 
        : allBookings.filter(b => b.status === status);
    
    const bookingsList = document.getElementById('bookingsList');
    const noBookings = document.getElementById('noBookings');
    
    bookingsList.innerHTML = '';
    noBookings.style.display = 'none';
    
    if (filtered.length === 0) {
        noBookings.style.display = 'block';
        return;
    }
    
    filtered.forEach(booking => {
        const card = createBookingCard(booking);
        bookingsList.appendChild(card);
    });
}

function viewBooking(bookingId) {
    alert('Booking details feature coming soon!\n\nBooking ID: ' + bookingId);
}

async function cancelBookingConfirm(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }
    
    const reason = prompt('Please provide a reason for cancellation (optional):');
    
    try {
        await cancelBooking(bookingId, reason || '');
        alert('Booking cancelled successfully!');
        loadBookings();
    } catch (error) {
        console.error('Error cancelling booking:', error);
        alert('Failed to cancel booking: ' + error.message);
    }
}
