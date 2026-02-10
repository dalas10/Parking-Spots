// Home page functionality
let allSpots = [];
let currentFilters = {};
let map = null;
let markers = [];
let currentView = 'map';

// Load parking spots on page load
document.addEventListener('DOMContentLoaded', () => {
    // Try to restore previous filter values from localStorage
    const savedDate = localStorage.getItem('filterStartDate');
    const savedTime = localStorage.getItem('filterStartTime');
    const savedDuration = localStorage.getItem('filterDuration');
    
    if (savedDate && savedTime && savedDuration) {
        // Restore saved filters
        document.getElementById('filterStartDate').value = savedDate;
        document.getElementById('filterStartTime').value = savedTime;
        document.getElementById('filterDuration').value = savedDuration;
    } else {
        // Set default date/time filters to current time + 1 hour duration
        const now = new Date();
        document.getElementById('filterStartDate').value = now.toISOString().split('T')[0];
        document.getElementById('filterStartTime').value = now.toTimeString().slice(0, 5);
        document.getElementById('filterDuration').value = '1';
    }
    
    // Add Enter key handler for search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchParking();
            }
        });
    }
    
    initializeMap();
    loadParkingSpots();
    loadStats();
});

// Reload dynamic content when language changes
document.addEventListener('languageChanged', () => {
    if (allSpots.length > 0) {
        // Reload map markers with new translations
        updateMapWithSpots(allSpots);
        
        // Reload spot cards with new translations
        const spotsGrid = document.getElementById('spotsGrid');
        if (spotsGrid && currentView === 'list') {
            spotsGrid.innerHTML = '';
            allSpots.forEach(spot => {
                const card = createSpotCard(spot);
                spotsGrid.appendChild(card);
            });
        }
    }
});

function initializeMap() {
    // Initialize map centered on New York City
    map = L.map('map').setView([40.7589, -73.9851], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
}

function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

function addMarkerForSpot(spot) {
    const marker = L.marker([spot.latitude, spot.longitude])
        .addTo(map);
    
    const features = [];
    if (spot.is_covered) features.push('🏠 ' + (window.t ? t('filters.covered') : 'Covered'));
    if (spot.has_ev_charging) features.push('⚡ EV');
    if (spot.has_security) features.push('🔒 Secure');
    
    const reviewsText = spot.total_reviews > 0 
        ? `${spot.total_reviews} ${window.t ? t('spot.reviews') : 'reviews'}`
        : (window.t ? t('spot.no_reviews') : 'No reviews yet');
    
    // Build URL with filter parameters
    const startDate = document.getElementById('filterStartDate')?.value;
    const startTime = document.getElementById('filterStartTime')?.value;
    const duration = document.getElementById('filterDuration')?.value;
    
    let spotUrl = `spot.html?id=${spot.id}`;
    if (startDate && startTime && duration) {
        spotUrl += `&date=${startDate}&time=${startTime}&duration=${duration}`;
    }
    
    const popupContent = `
        <div class="map-popup">
            <h3>${spot.title}</h3>
            <p>📍 ${spot.city}, ${spot.state}</p>
            ${features.length > 0 ? `<p>${features.join(' • ')}</p>` : ''}
            <div class="price">${formatCurrency(spot.hourly_rate)}${window.t ? t('spot.per_hour') : '/hr'}</div>
            ${spot.average_rating ? `<p>⭐ ${spot.average_rating.toFixed(1)} (${reviewsText})</p>` : ''}
            <a href="${spotUrl}" class="btn-view" onclick="if ('${startDate}') localStorage.setItem('filterStartDate', '${startDate}'); if ('${startTime}') localStorage.setItem('filterStartTime', '${startTime}'); if ('${duration}') localStorage.setItem('filterDuration', '${duration}');">${window.t ? t('bookings.view_details') : 'View Details'}</a>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    markers.push(marker);
}

function updateMapWithSpots(spots) {
    clearMarkers();
    
    if (spots.length === 0) return;
    
    // Add markers for each spot
    spots.forEach(spot => addMarkerForSpot(spot));
    
    // Fit map to show all markers
    if (spots.length > 0) {
        const bounds = L.latLngBounds(spots.map(s => [s.latitude, s.longitude]));
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

function switchView(view) {
    currentView = view;
    
    const mapContainer = document.getElementById('mapContainer');
    const listContainer = document.getElementById('listContainer');
    const btnMapView = document.getElementById('btnMapView');
    const btnListView = document.getElementById('btnListView');
    
    if (view === 'map') {
        mapContainer.style.display = 'block';
        listContainer.style.display = 'none';
        btnMapView.classList.add('active');
        btnListView.classList.remove('active');
        
        // Refresh map size after display change
        setTimeout(() => map.invalidateSize(), 100);
    } else {
        mapContainer.style.display = 'none';
        listContainer.style.display = 'block';
        btnMapView.classList.remove('active');
        btnListView.classList.add('active');
    }
}

// Apply filters function that works for both views
function applyFilters() {
    loadParkingSpots();
}

// Clear all filters
function clearFilters() {
    console.log('clearFilters() called');
    
    // Clear localStorage
    localStorage.removeItem('filterStartDate');
    localStorage.removeItem('filterStartTime');
    localStorage.removeItem('filterDuration');
    
    // Reset to default values (current time)
    const now = new Date();
    const dateInput = document.getElementById('filterStartDate');
    const timeInput = document.getElementById('filterStartTime');
    const durationInput = document.getElementById('filterDuration');
    
    if (dateInput) dateInput.value = now.toISOString().split('T')[0];
    if (timeInput) timeInput.value = now.toTimeString().slice(0, 5);
    if (durationInput) durationInput.value = '1';
    
    // Clear other filters
    const citySelect = document.getElementById('filterCity');
    const typeSelect = document.getElementById('filterType');
    const evCheckbox = document.getElementById('filterEV');
    const coveredCheckbox = document.getElementById('filterCovered');
    
    if (citySelect) citySelect.value = '';
    if (typeSelect) typeSelect.value = '';
    if (evCheckbox) evCheckbox.checked = false;
    if (coveredCheckbox) coveredCheckbox.checked = false;
    
    // Clear search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
    }
    
    console.log('Filters cleared, reloading spots...');
    
    // Reload spots with cleared filters
    loadParkingSpots();
}

async function loadParkingSpots() {
    const loadingSpots = document.getElementById('loadingSpots');
    const spotsGrid = document.getElementById('spotsGrid');
    const noSpots = document.getElementById('noSpots');
    const filterCity = document.getElementById('filterCity');
    
    loadingSpots.style.display = 'block';
    spotsGrid.innerHTML = '';
    noSpots.style.display = 'none';
    
    try {
        // Get filter values
        const startDate = document.getElementById('filterStartDate')?.value;
        const startTime = document.getElementById('filterStartTime')?.value;
        const duration = document.getElementById('filterDuration')?.value;
        
        // Save filter values to localStorage
        if (startDate) localStorage.setItem('filterStartDate', startDate);
        if (startTime) localStorage.setItem('filterStartTime', startTime);
        if (duration) localStorage.setItem('filterDuration', duration);
        
        const filters = {
            city: filterCity?.value || '',
            spot_type: document.getElementById('filterType')?.value || '',
            has_ev_charging: document.getElementById('filterEV')?.checked || undefined,
            is_covered: document.getElementById('filterCovered')?.checked || undefined,
            limit: 50
        };
        
        // Add start_time and calculate end_time if all values are provided
        if (startDate && startTime && duration) {
            const startDateTime = new Date(`${startDate}T${startTime}`);
            filters.start_time = startDateTime.toISOString();
            
            // Calculate end time by adding duration hours
            const endDateTime = new Date(startDateTime);
            endDateTime.setHours(endDateTime.getHours() + parseInt(duration));
            filters.end_time = endDateTime.toISOString();
        }
        
        // Remove undefined values
        Object.keys(filters).forEach(key => 
            filters[key] === undefined && delete filters[key]
        );
        
        const spots = await searchParkingSpots(filters);
        allSpots = spots;
        
        loadingSpots.style.display = 'none';
        
        if (spots.length === 0) {
            noSpots.style.display = 'block';
            return;
        }
        
        // Update map with markers
        updateMapWithSpots(spots);
        
        // Populate city filter if empty
        if (filterCity && filterCity.options.length === 1) {
            const cities = [...new Set(spots.map(s => s.city))];
            cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                filterCity.appendChild(option);
            });
        }
        
        // Display spots
        spots.forEach(spot => {
            const card = createSpotCard(spot);
            spotsGrid.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading spots:', error);
        loadingSpots.style.display = 'none';
        noSpots.style.display = 'block';
        noSpots.innerHTML = `<p>Error loading parking spots: ${error.message}</p>`;
    }
}

function createSpotCard(spot) {
    const card = document.createElement('div');
    card.className = 'spot-card';
    
    // Get current filter values to pass to spot details
    const startDate = document.getElementById('filterStartDate')?.value;
    const startTime = document.getElementById('filterStartTime')?.value;
    const duration = document.getElementById('filterDuration')?.value;
    
    // Build URL with query parameters
    let spotUrl = `spot.html?id=${spot.id}`;
    if (startDate && startTime && duration) {
        spotUrl += `&date=${startDate}&time=${startTime}&duration=${duration}`;
    }
    
    card.onclick = () => {
        // Save filter values to localStorage before navigating
        if (startDate) localStorage.setItem('filterStartDate', startDate);
        if (startTime) localStorage.setItem('filterStartTime', startTime);
        if (duration) localStorage.setItem('filterDuration', duration);
        window.location.href = spotUrl;
    };
    
    const features = [];
    if (spot.is_covered) features.push(window.t ? t('filters.covered') : 'Covered');
    if (spot.has_ev_charging) features.push(window.t ? t('filters.ev_charging') : 'EV Charging');
    if (spot.has_security) features.push('Security');
    if (spot.is_handicap_accessible) features.push('Accessible');
    
    const reviewsText = spot.total_reviews > 0 
        ? `${spot.total_reviews} ${window.t ? t('spot.reviews') : 'reviews'}`
        : (window.t ? t('spot.no_reviews') : '');
    
    card.innerHTML = `
        <div class="spot-image">🅿️</div>
        <div class="spot-content">
            <div class="spot-title">${spot.title}</div>
            <div class="spot-location">📍 ${spot.city}, ${spot.state}</div>
            <div class="spot-features">
                ${features.map(f => `<span class="feature-badge">${f}</span>`).join('')}
            </div>
            <div class="spot-price">${formatCurrency(spot.hourly_rate)}${window.t ? t('spot.per_hour') : '/hr'}</div>
            ${spot.average_rating ? `
                <div class="spot-rating">
                    ⭐ ${spot.average_rating.toFixed(1)} (${reviewsText})
                </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

async function searchParking() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (!query) {
        loadParkingSpots();
        return;
    }
    
    const loadingSpots = document.getElementById('loadingSpots');
    const spotsGrid = document.getElementById('spotsGrid');
    const noSpots = document.getElementById('noSpots');
    
    loadingSpots.style.display = 'block';
    spotsGrid.innerHTML = '';
    noSpots.style.display = 'none';
    
    try {
        // Search across all spots without other filters
        const spots = await searchParkingSpots({ limit: 100 });
        
        // Filter by search query
        const filtered = spots.filter(spot => 
            spot.title.toLowerCase().includes(query.toLowerCase()) ||
            spot.city.toLowerCase().includes(query.toLowerCase()) ||
            spot.zip_code.includes(query) ||
            spot.address.toLowerCase().includes(query.toLowerCase())
        );
        
        allSpots = filtered;
        loadingSpots.style.display = 'none';
        
        if (filtered.length === 0) {
            noSpots.style.display = 'block';
            // Clear map markers if no results
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];
            return;
        }
        
        // Update list view
        filtered.forEach(spot => {
            const card = createSpotCard(spot);
            spotsGrid.appendChild(card);
        });
        
        // Update map view with filtered results
        updateMapWithSpots(filtered);
    } catch (error) {
        console.error('Search error:', error);
        loadingSpots.style.display = 'none';
        noSpots.style.display = 'block';
    }
}

async function loadStats() {
    try {
        const spots = await searchParkingSpots({ limit: 100 });
        
        document.getElementById('totalSpots').textContent = spots.length;
        
        const cities = new Set(spots.map(s => s.city));
        document.getElementById('totalCities').textContent = cities.size;
        
        if (spots.length > 0) {
            const avgPrice = spots.reduce((sum, s) => sum + s.hourly_rate, 0) / spots.length;
            document.getElementById('avgPrice').textContent = formatCurrency(avgPrice);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}
