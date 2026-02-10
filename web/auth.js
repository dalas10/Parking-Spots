// API Configuration
// Auto-detect: use localhost if accessed locally, otherwise use server IP
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `http://${window.location.hostname}:8000`;

// Auth Helper Functions
function isAuthenticated() {
    return !!localStorage.getItem('token');
}

function getToken() {
    return localStorage.getItem('token');
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// Update navigation based on auth state
function updateNav() {
    const navLogin = document.getElementById('navLogin');
    const navBookings = document.getElementById('navBookings');
    const navProfile = document.getElementById('navProfile');
    const btnLogout = document.getElementById('btnLogout');
    
    if (isAuthenticated()) {
        if (navLogin) navLogin.style.display = 'none';
        if (navBookings) navBookings.style.display = 'block';
        if (navProfile) navProfile.style.display = 'block';
        if (btnLogout) {
            btnLogout.style.display = 'block';
            btnLogout.onclick = logout;
        }
    } else {
        if (navLogin) navLogin.style.display = 'block';
        if (navBookings) navBookings.style.display = 'none';
        if (navProfile) navProfile.style.display = 'none';
        if (btnLogout) btnLogout.style.display = 'none';
    }
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', updateNav);
