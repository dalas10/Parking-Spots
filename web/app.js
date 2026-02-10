// Home page functionality
let allSpots = [];
let currentFilters = {};
let map = null;
let markers = [];
let currentView = 'map';

// Load parking spots on page load
document.addEventListener('DOMContentLoaded', () => {
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
    
    const popupContent = `
        <div class="map-popup">
            <h3>${spot.title}</h3>
            <p>📍 ${spot.city}, ${spot.state}</p>
            ${features.length > 0 ? `<p>${features.join(' • ')}</p>` : ''}
            <div class="price">${formatCurrency(spot.hourly_rate)}${window.t ? t('spot.per_hour') : '/hr'}</div>
            ${spot.average_rating ? `<p>⭐ ${spot.average_rating.toFixed(1)} (${reviewsText})</p>` : ''}
            <a href="spot.html?id=${spot.id}" class="btn-view">${window.t ? t('bookings.view_details') : 'View Details'}</a>
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
    card.onclick = () => window.location.href = `spot.html?id=${spot.id}`;
    
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
    
    // Filter spots by search query
    const filtered = allSpots.filter(spot => 
        spot.title.toLowerCase().includes(query.toLowerCase()) ||
        spot.city.toLowerCase().includes(query.toLowerCase()) ||
        spot.zip_code.includes(query) ||
        spot.address.toLowerCase().includes(query.toLowerCase())
    );
    
    const spotsGrid = document.getElementById('spotsGrid');
    const noSpots = document.getElementById('noSpots');
    
    spotsGrid.innerHTML = '';
    noSpots.style.display = 'none';
    
    if (filtered.length === 0) {
        noSpots.style.display = 'block';
        return;
    }
    
    filtered.forEach(spot => {
        const card = createSpotCard(spot);
        spotsGrid.appendChild(card);
    });
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
