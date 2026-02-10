# ParkingSpots Web Frontend

## 🌐 Web Application

A simple, modern web interface for the ParkingSpots platform. Browse, search, and book parking spots directly from your browser.

## 🚀 Quick Start

The web server is already running!

**Access the application:**
- **Home Page**: http://localhost:3000
- **Login**: http://localhost:3000/login.html
- **Register**: http://localhost:3000/register.html

## 📱 Features

### Public Pages
- **Home** - Browse all available parking spots
- **Search** - Filter by city, type, amenities
- **Spot Details** - View full information, photos, reviews
- **Login/Register** - Create account or sign in

### Authenticated Pages
- **My Bookings** - View and manage your bookings
- **Profile** - View account information and statistics
- **Book Parking** - Make reservations (requires login)

## 🔑 Demo Accounts

### Renter Account
```
Email: renter1@parkingspots.com
Password: Renter123!
```

### Owner Account
```
Email: owner1@parkingspots.com
Password: Owner123!
```

## 🎯 How to Use

### 1. Browse Parking Spots
- Go to http://localhost:3000
- See all available parking spots in NYC
- Use filters to narrow down results:
  - Filter by city
  - Filter by type (Covered, Garage, Outdoor, etc.)
  - Filter by amenities (EV Charging, Covered)

### 2. View Spot Details
- Click on any parking spot card
- See full description, amenities, location
- View pricing (hourly, daily, monthly)
- Read reviews from other users

### 3. Make a Booking
- Click "Book Now" on a spot (must be logged in)
- Select start and end date/time
- Enter vehicle information
- Review booking summary with total cost
- Confirm booking

### 4. Manage Bookings
- Go to "My Bookings" in navigation
- View all your bookings (upcoming, active, completed)
- Filter by status
- Cancel upcoming bookings if needed

### 5. View Your Profile
- Click "Profile" in navigation
- See your account information
- View booking statistics
- Check total spent

## 🛠️ Technical Details

### Stack
- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **No build tools required** - Just open in browser
- **Backend API**: FastAPI (http://localhost:8000)

### Files
```
web/
├── index.html          # Home page with map view
├── login.html          # Login page
├── register.html       # Registration page
├── spot.html          # Parking spot details
├── bookings.html      # My bookings
├── profile.html       # User profile
├── styles.css         # All CSS styles
├── auth.js           # Authentication logic
├── api.js            # API calls and helpers
├── app.js            # Home page functionality
├── spot-details.js   # Spot details page
├── bookings.js       # Bookings page
├── profile.js        # Profile page
├── i18n.js           # Internationalization module
├── translations.json  # Language translations (EN/EL)
├── README.md         # This file
└── I18N.md           # i18n documentation
```

### Multi-Language Support 🌍
The application includes a complete internationalization system:
- **Languages**: English 🇬🇧 and Greek 🇬🇷
- **Auto-switching**: Language selector in navigation bar
- **Persistent**: User preference saved in localStorage
- **Modular**: JSON-based translation system
- **Dynamic**: Real-time updates for all content

See [I18N.md](I18N.md) for full documentation.

### API Integration
- Connects to backend at `http://localhost:8000`
- JWT token authentication
- All API calls handled via `api.js`
- Automatic auth token management

## 🔧 Starting/Stopping the Server

### Start Web Server
```bash
cd /home/dalas/ParkingSpots/web
python3 -m http.server 3000
```

### Stop Web Server
Press `Ctrl+C` in the terminal where it's running

### Backend Must Be Running
Make sure FastAPI backend is running on port 8000:
```bash
cd /home/dalas/ParkingSpots/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 What You Can Test

1. **User Registration** - Create a new account (renter or owner)
2. **User Login** - Sign in with demo accounts
3. **Browse Spots** - See all 6 parking spots from database
4. **Search & Filter** - Filter by city, type, amenities
5. **View Details** - See spot information, reviews, pricing
6. **Make Booking** - Book a spot with vehicle info
7. **View Bookings** - See your active/upcoming/past bookings
8. **Cancel Booking** - Cancel an upcoming reservation
9. **View Profile** - See your stats and account info
10. **Logout** - Sign out and return to home

## 🎨 Design Features

- Modern, clean interface
- Responsive design (desktop & mobile friendly)
- Smooth transitions and animations
- Color-coded status badges
- Interactive cards and buttons
- Loading states for async operations
- Error handling and user feedback

## 🔒 Security

- JWT token stored in localStorage
- Automatic token validation
- Redirect to login if unauthorized
- Secure API communication
- CORS enabled on backend

## 💡 Tips

- Open browser DevTools (F12) to see API calls
- Check Console for any errors
- Network tab shows all requests to backend
- LocalStorage shows saved auth tokens

## 📝 Next Steps

To continue developing:
1. Add payment processing UI
2. Add owner dashboard pages
3. Add parking spot creation/editing
4. Add real-time availability updates
5. Add map integration (Google Maps)
6. Add photo upload functionality
7. Add messaging between users
8. Add push notifications

## 🐛 Troubleshooting

**Can't access http://localhost:3000?**
- Make sure web server is running (check terminal)
- Try http://127.0.0.1:3000 instead

**API calls failing?**
- Ensure backend is running on port 8000
- Check backend logs for errors
- Open http://localhost:8000/docs to verify backend

**Login not working?**
- Use exact email and password from demo accounts
- Check browser console for errors
- Clear localStorage and try again

**No parking spots showing?**
- Make sure database is populated
- Check backend is running
- Open browser DevTools Network tab

---

**Enjoy testing ParkingSpots! 🅿️**
