// Profile page
document.addEventListener('DOMContentLoaded', () => {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    
    loadProfile();
});

async function loadProfile() {
    try {
        const user = await getUserProfile();
        
        // Save updated user info
        localStorage.setItem('user', JSON.stringify(user));
        
        // Display user info
        document.getElementById('userName').textContent = user.full_name;
        document.getElementById('userEmail').textContent = user.email;
        document.getElementById('userRole').textContent = user.role.toUpperCase();
        
        // Avatar
        const avatar = document.getElementById('userAvatar');
        if (user.profile_image) {
            avatar.innerHTML = `<img src="${user.profile_image}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
        } else {
            avatar.textContent = user.full_name.charAt(0).toUpperCase();
        }
        
        // Account information
        document.getElementById('infoName').textContent = user.full_name;
        document.getElementById('infoEmail').textContent = user.email;
        document.getElementById('infoPhone').textContent = user.phone_number || (window.t ? t('profile.not_provided') : 'Not provided');
        document.getElementById('infoRole').textContent = user.role.toUpperCase();
        document.getElementById('infoStatus').textContent = user.is_active ? (window.t ? t('profile.active') : '✅ Active') : (window.t ? t('profile.inactive') : '❌ Inactive');
        document.getElementById('infoVerified').textContent = user.is_verified ? (window.t ? t('profile.verified_yes') : '✅ Verified') : (window.t ? t('profile.verified_no') : '❌ Not Verified');
        
        // Format created date
        const createdDate = new Date(user.created_at);
        document.getElementById('infoCreated').textContent = createdDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        // Load statistics
        await loadUserStats();
        
    } catch (error) {
        console.error('Error loading profile:', error);
        alert('Failed to load profile: ' + error.message);
    }
}

async function loadUserStats() {
    const userStats = document.getElementById('userStats');
    
    try {
        // Get user's bookings
        const bookings = await getMyBookings();
        
        const totalBookings = bookings.length;
        const activeBookings = bookings.filter(b => b.status === 'in_progress').length;
        const completedBookings = bookings.filter(b => b.status === 'completed').length;
        const upcomingBookings = bookings.filter(b => b.status === 'confirmed').length;
        
        // Calculate total spent
        const totalSpent = bookings
            .filter(b => b.status !== 'cancelled')
            .reduce((sum, b) => sum + b.total_amount, 0);
        
        userStats.innerHTML = `
            <div class="stat-box">
                <div class="stat-value">${totalBookings}</div>
                <div class="stat-name">${window.t ? t('profile.total_bookings') : 'Total Bookings'}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${activeBookings}</div>
                <div class="stat-name">${window.t ? t('profile.active_bookings') : 'Active'}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${upcomingBookings}</div>
                <div class="stat-name">${window.t ? t('profile.upcoming_bookings') : 'Upcoming'}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${completedBookings}</div>
                <div class="stat-name">${window.t ? t('profile.completed_bookings') : 'Completed'}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${formatCurrency(totalSpent)}</div>
                <div class="stat-name">${window.t ? t('profile.total_spent') : 'Total Spent'}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${formatCurrency(totalSpent / Math.max(completedBookings, 1))}</div>
                <div class="stat-name">${window.t ? t('profile.avg_booking') : 'Avg per Booking'}</div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading stats:', error);
        userStats.innerHTML = '<p>Unable to load statistics</p>';
    }
}

function handleLogout() {
    const confirmMsg = window.t ? t('messages.sign_out_confirm') : 'Are you sure you want to sign out?';
    if (confirm(confirmMsg)) {
        logout();
    }
}
