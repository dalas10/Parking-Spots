// Spot details page
let currentSpot = null;

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const spotId = urlParams.get('id');
    
    if (!spotId) {
        window.location.href = 'index.html';
        return;
    }
    
    loadSpotDetails(spotId);
    
    // Update cost when times change
    document.getElementById('startTime').addEventListener('change', updateBookingSummary);
    document.getElementById('endTime').addEventListener('change', updateBookingSummary);
});

async function loadSpotDetails(spotId) {
    const loadingSpot = document.getElementById('loadingSpot');
    const spotDetails = document.getElementById('spotDetails');
    
    loadingSpot.style.display = 'flex';
    spotDetails.style.display = 'none';
    
    try {
        const spot = await getParkingSpot(spotId);
        currentSpot = spot;
        
        // Update page title
        document.getElementById('spotTitle').textContent = spot.title;
        document.getElementById('spotDescription').textContent = spot.description || 'No description available.';
        
        // Display images
        const spotImages = document.getElementById('spotImages');
        if (spot.images && spot.images.length > 0) {
            spotImages.innerHTML = `<img src="${spot.images[0]}" alt="${spot.title}" style="width:100%;height:100%;object-fit:cover;border-radius:0.75rem;">`;
        } else {
            spotImages.innerHTML = '<div style="font-size:6rem;">🅿️</div>';
        }
        
        // Display amenities
        const amenities = [];
        if (spot.is_covered) amenities.push('🏠 Covered');
        if (spot.has_ev_charging) amenities.push('⚡ EV Charging');
        if (spot.has_security) amenities.push('🔒 Security');
        if (spot.has_lighting) amenities.push('💡 Well-lit');
        if (spot.is_handicap_accessible) amenities.push('♿ Accessible');
        
        const spotAmenities = document.getElementById('spotAmenities');
        spotAmenities.innerHTML = amenities.map(a => `<span class="amenity-tag">${a}</span>`).join('');
        
        // Display address
        document.getElementById('spotAddress').textContent = 
            `${spot.address}, ${spot.city}, ${spot.state} ${spot.zip_code}`;
        
        // Initialize map
        const spotMap = L.map('spotMap').setView([spot.latitude, spot.longitude], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(spotMap);
        
        // Add marker
        L.marker([spot.latitude, spot.longitude])
            .addTo(spotMap)
            .bindPopup(`<b>${spot.title}</b><br>${spot.address}`)
            .openPopup();
        
        // Display pricing
        const spotPricing = document.getElementById('spotPricing');
        spotPricing.innerHTML = `
            <div class="price-item">
                <span>${window.t ? t('spot.hourly') : 'Hourly'}</span>
                <strong>${formatCurrency(spot.hourly_rate)}</strong>
            </div>
            ${spot.daily_rate ? `
                <div class="price-item">
                    <span>${window.t ? t('spot.daily') : 'Daily'}</span>
                    <strong>${formatCurrency(spot.daily_rate)}</strong>
                </div>
            ` : ''}
            ${spot.monthly_rate ? `
                <div class="price-item">
                    <span>${window.t ? t('spot.monthly') : 'Monthly'}</span>
                    <strong>${formatCurrency(spot.monthly_rate)}</strong>
                </div>
            ` : ''}
        `;
        
        // Display rating
        const spotRating = document.getElementById('spotRating');
        if (spot.average_rating && spot.total_reviews > 0) {
            const reviewText = window.t ? t('spot.reviews') : 'reviews';
            spotRating.innerHTML = `
                <span>⭐ ${spot.average_rating.toFixed(1)}</span>
                <span>(${spot.total_reviews} ${reviewText})</span>
            `;
        } else {
            spotRating.innerHTML = `<span>${window.t ? t('spot.no_reviews') : 'No reviews yet'}</span>`;
        }
        
        // Load reviews
        loadReviews(spotId);
        
        // Check if user is logged in for booking
        if (!isAuthenticated()) {
            const loginText = window.t ? t('spot.login_to_book') : 'Login to Book';
            document.getElementById('bookingForm').innerHTML = `
                <p style="text-align:center;padding:2rem;">
                    <a href="login.html" class="btn-primary btn-full">${loginText}</a>
                </p>
            `;
        }
        
        loadingSpot.style.display = 'none';
        spotDetails.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading spot:', error);
        loadingSpot.innerHTML = `<p>Error loading parking spot: ${error.message}</p>`;
    }
}

async function loadReviews(spotId) {
    const spotReviews = document.getElementById('spotReviews');
    
    try {
        const reviews = await getSpotReviews(spotId);
        
        if (reviews.length === 0) {
            spotReviews.innerHTML = '<p>No reviews yet.</p>';
            return;
        }
        
        spotReviews.innerHTML = reviews.map(review => `
            <div class="review-item">
                <div class="review-header">
                    <span class="review-author">${review.reviewer?.full_name || 'Anonymous'}</span>
                    <span class="review-date">${formatDate(review.created_at)}</span>
                </div>
                <div class="rating">⭐ ${review.overall_rating}/5</div>
                ${review.title ? `<h4>${review.title}</h4>` : ''}
                <p>${review.comment}</p>
                ${review.owner_response ? `
                    <div style="margin-top:0.5rem;padding:0.75rem;background:var(--bg-light);border-radius:0.5rem;">
                        <strong>Owner Response:</strong><br>
                        ${review.owner_response}
                    </div>
                ` : ''}
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading reviews:', error);
        spotReviews.innerHTML = '<p>Unable to load reviews.</p>';
    }
}

function updateBookingSummary() {
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    const bookingSummary = document.getElementById('bookingSummary');
    
    if (!startTime || !endTime || !currentSpot) {
        bookingSummary.style.display = 'none';
        return;
    }
    
    const hours = calculateDuration(startTime, endTime);
    
    if (hours <= 0) {
        bookingSummary.style.display = 'none';
        return;
    }
    
    const { subtotal, serviceFee, total } = calculateBookingCost(currentSpot.hourly_rate, hours);
    
    const hoursText = window.t ? t('booking.hours') : 'hours';
    document.getElementById('duration').textContent = `${hours} ${hoursText}`;
    document.getElementById('subtotal').textContent = formatCurrency(subtotal);
    document.getElementById('serviceFee').textContent = formatCurrency(serviceFee);
    document.getElementById('total').textContent = formatCurrency(total);
    
    bookingSummary.style.display = 'block';
}

async function handleBooking(e) {
    e.preventDefault();
    
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    const vehiclePlate = document.getElementById('vehiclePlate').value;
    const vehicleMake = document.getElementById('vehicleMake').value;
    const vehicleModel = document.getElementById('vehicleModel').value;
    const vehicleColor = document.getElementById('vehicleColor').value;
    
    const btnBook = document.getElementById('btnBook');
    btnBook.disabled = true;
    btnBook.textContent = 'Processing...';
    
    try {
        const booking = await createBooking({
            parking_spot_id: currentSpot.id,
            start_time: new Date(startTime).toISOString(),
            end_time: new Date(endTime).toISOString(),
            vehicle_plate: vehiclePlate,
            vehicle_make: vehicleMake,
            vehicle_model: vehicleModel,
            vehicle_color: vehicleColor
        });
        
        alert('Booking successful! Redirecting to your bookings...');
        window.location.href = 'bookings.html';
        
    } catch (error) {
        console.error('Booking error:', error);
        alert('Booking failed: ' + error.message);
        btnBook.disabled = false;
        btnBook.textContent = 'Book Now';
    }
}
