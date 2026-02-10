# ParkingSpots Testing Guide

Complete guide to set up, run, and test the entire ParkingSpots platform.

---

## Prerequisites

### Required Software
- **Python 3.11+** - For backend
- **Node.js 18+** - For mobile app
- **PostgreSQL 14+** - Database
- **Redis** (optional) - For real-time features
- **Docker** (optional) - For containerized setup

### Accounts Needed
- **Stripe Account** - Get test API keys from https://stripe.com
- **Expo Account** (optional) - For mobile testing

---

## Part 1: Backend Setup & Testing

### Step 1.1: Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download installer from https://www.postgresql.org/download/windows/

### Step 1.2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE parkingspots;
CREATE USER parkinguser WITH PASSWORD 'parkingpass123';
GRANT ALL PRIVILEGES ON DATABASE parkingspots TO parkinguser;
\q
```

### Step 1.3: Set Up Backend Environment

```bash
cd /home/dalas/ParkingSpots/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 1.4: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimum .env configuration:**
```env
DATABASE_URL=postgresql+asyncpg://parkinguser:parkingpass123@localhost:5432/parkingspots
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Test Keys (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Optional: Redis for real-time features
REDIS_URL=redis://localhost:6379
```

### Step 1.5: Run Database Migrations

```bash
# Initialize Alembic (if not done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial setup"

# Apply migrations
alembic upgrade head
```

### Step 1.6: Start Backend Server

```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 1.7: Test Backend API

**Open another terminal and test:**

```bash
# 1. Health check
curl http://localhost:8000/

# Expected: {"status":"healthy","message":"ParkingSpots API"}

# 2. Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "phone_number": "+1234567890"
  }'

# Expected: Returns user object with ID and email

# 3. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123!"

# Expected: Returns access_token and token_type
# SAVE THIS TOKEN for next steps!

# 4. Get current user (replace YOUR_TOKEN with token from step 3)
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: Returns your user profile

# 5. View API documentation
# Open browser: http://localhost:8000/docs
```

### Step 1.8: Test Backend with Interactive Docs

1. **Open browser:** http://localhost:8000/docs
2. **You'll see Swagger UI** with all API endpoints
3. **Click "Authorize"** button (top right)
4. **Login to get token:**
   - Use `/api/v1/auth/login` endpoint
   - Enter your email/password
   - Copy the `access_token` from response
5. **Click "Authorize" again** and paste: `Bearer YOUR_TOKEN`
6. **Now test any endpoint** by clicking "Try it out"

**Key endpoints to test:**
- ✅ `POST /api/v1/auth/register` - Create account
- ✅ `POST /api/v1/auth/login` - Login
- ✅ `GET /api/v1/users/me` - Get profile
- ✅ `POST /api/v1/parking-spots` - Create parking spot
- ✅ `GET /api/v1/parking-spots/search` - Search spots
- ✅ `POST /api/v1/bookings` - Create booking
- ✅ `GET /api/v1/bookings/my-bookings` - View bookings

---

## Part 2: Mobile App Setup & Testing

### Step 2.1: Install Node.js and Expo CLI

```bash
# Verify Node.js installation
node --version  # Should be 18+
npm --version

# Install Expo CLI globally
npm install -g expo-cli eas-cli
```

### Step 2.2: Set Up Mobile App

```bash
cd /home/dalas/ParkingSpots/mobile

# Install dependencies
npm install

# Or if you prefer yarn
yarn install
```

### Step 2.3: Configure Mobile Environment

```bash
# Create environment file
nano .env
```

**Add your configuration:**
```env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

**For testing on physical device:**
- Replace `localhost` with your computer's IP address
- Find IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
- Example: `http://192.168.1.100:8000/api/v1`

### Step 2.4: Start Mobile App

```bash
# Start Expo development server
npx expo start
```

**Expected output:**
```
› Metro waiting on exp://192.168.1.100:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

### Step 2.5: Test on Device or Simulator

**Option A: Physical Device (Recommended)**
1. Install **Expo Go** app:
   - iOS: https://apps.apple.com/app/expo-go/id982107779
   - Android: https://play.google.com/store/apps/details?id=host.exp.exponent
2. Open Expo Go
3. Scan QR code from terminal
4. App should load on your device

**Option B: iOS Simulator (Mac only)**
```bash
# Press 'i' in the Expo terminal
# Or:
npx expo start --ios
```

**Option C: Android Emulator**
```bash
# Make sure Android Studio is installed with an emulator
# Press 'a' in the Expo terminal
# Or:
npx expo start --android
```

### Step 2.6: Test Mobile App Features

Once the app loads, test these flows:

#### A. Authentication Flow
1. **Register new account**
   - Tap "Sign Up"
   - Enter email, password, name, phone
   - Submit
   - ✅ Should navigate to home screen

2. **Logout and Login**
   - Go to Profile
   - Tap "Logout"
   - Tap "Sign In"
   - Enter credentials
   - ✅ Should login successfully

#### B. Create Parking Spot (Owner Flow)
1. **Navigate to "List Your Spot"**
2. **Fill in details:**
   - Title: "Downtown Parking"
   - Description: "Covered parking near station"
   - Address: "123 Main St"
   - Price: $5/hour
   - Add amenities (covered, EV charging, etc.)
3. **Submit**
4. ✅ Should create spot and show on map

#### C. Search & Book Parking (Driver Flow)
1. **On home screen:**
   - See map with parking markers
   - Pan/zoom to see different spots
2. **Search:**
   - Enter location in search bar
   - Apply filters (price, amenities)
   - ✅ Should show matching spots
3. **Book a spot:**
   - Tap on a marker
   - View spot details
   - Select date/time
   - Tap "Book Now"
   - ✅ Should show price breakdown
4. **Complete payment:**
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/28)
   - CVC: Any 3 digits (e.g., 123)
   - ✅ Should confirm booking

#### D. View Bookings
1. **Go to Profile → My Bookings**
2. ✅ Should see your booking
3. **Check booking details**
4. ✅ Should show spot info, dates, price

#### E. Reviews
1. **After booking, leave review:**
   - Go to completed booking
   - Tap "Leave Review"
   - Rate 5 stars
   - Write comment
   - Submit
2. ✅ Review should appear on spot details

---

## Part 3: Integration Testing

### Test 3.1: End-to-End Booking Flow

**Complete flow from both perspectives:**

1. **Device 1 (Owner):**
   - Login as user A
   - Create parking spot at specific location
   - Note the spot details

2. **Device 2 (Driver):**
   - Login as user B
   - Search for the spot created by user A
   - Book the spot for tomorrow
   - Complete payment with test card
   - ✅ Booking should succeed

3. **Back to Device 1 (Owner):**
   - Check notifications/bookings
   - ✅ Should see the new booking
   - View earnings dashboard
   - ✅ Should show expected earnings

### Test 3.2: Payment Flow

```bash
# Monitor backend logs while making payment
# In backend terminal, watch for:
```

1. ✅ Payment intent created
2. ✅ Payment confirmed
3. ✅ Booking status updated
4. ✅ Owner notified

### Test 3.3: Real-time Features

1. **Open app on two devices**
2. **Make booking on device 1**
3. **Check device 2** (if logged in as owner)
4. ✅ Should receive notification immediately

---

## Part 4: Database Verification

### Check Data in Database

```bash
# Connect to PostgreSQL
psql -U parkinguser -d parkingspots

# Check users
SELECT id, email, full_name, created_at FROM users;

# Check parking spots
SELECT id, title, price_per_hour, owner_id FROM parking_spots;

# Check bookings
SELECT id, spot_id, user_id, start_time, end_time, status, total_price 
FROM bookings;

# Check payments
SELECT id, booking_id, amount, status FROM payments;

# Exit
\q
```

---

## Part 5: Common Issues & Troubleshooting

### Issue 1: Backend won't start

**Error:** `asyncpg.exceptions.InvalidCatalogNameError`
```bash
# Database doesn't exist - create it:
psql postgres -c "CREATE DATABASE parkingspots;"
```

**Error:** `ModuleNotFoundError`
```bash
# Dependencies not installed:
pip install -r requirements.txt
```

### Issue 2: Mobile app can't connect to backend

**Problem:** API requests timeout or fail

**Solution 1:** Update API URL in mobile `.env`
```bash
# Find your IP address
ifconfig | grep "inet "  # Mac/Linux
ipconfig                 # Windows

# Use IP instead of localhost in mobile/.env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1
```

**Solution 2:** Check firewall
```bash
# Allow port 8000
sudo ufw allow 8000  # Linux
```

### Issue 3: Stripe payments fail

**Problem:** Payment intent creation fails

**Solution:** Verify Stripe keys
1. Check `.env` has correct test keys from Stripe dashboard
2. Keys should start with `sk_test_` and `pk_test_`
3. Restart backend after changing `.env`

### Issue 4: Database connection errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # Mac

# Restart if needed
sudo systemctl restart postgresql  # Linux
brew services restart postgresql   # Mac
```

### Issue 5: Alembic migration errors

```bash
# Reset migrations (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Or start fresh:
dropdb parkingspots
createdb parkingspots
alembic upgrade head
```

---

## Part 6: Quick Test Checklist

Use this checklist to verify everything works:

### Backend API ✅
- [ ] Server starts without errors
- [ ] Docs accessible at http://localhost:8000/docs
- [ ] User registration works
- [ ] User login returns token
- [ ] Protected endpoints require auth
- [ ] Can create parking spot
- [ ] Can search parking spots
- [ ] Can create booking
- [ ] Payment integration works

### Mobile App ✅
- [ ] App loads without errors
- [ ] Can register new account
- [ ] Can login
- [ ] Map displays correctly
- [ ] Can view parking spots on map
- [ ] Can search/filter spots
- [ ] Can view spot details
- [ ] Can create booking
- [ ] Payment flow works
- [ ] Can view booking history
- [ ] Can leave reviews
- [ ] Logout works

### Integration ✅
- [ ] Mobile app connects to backend
- [ ] Data syncs correctly
- [ ] Real-time updates work
- [ ] Payments process correctly
- [ ] Database stores all data
- [ ] Owner sees bookings
- [ ] Driver sees confirmed bookings

---

## Part 7: Advanced Testing

### Load Testing with pytest

```bash
cd backend
pytest tests/ -v
```

### API Testing with Postman

1. Import Postman collection (create one):
   - Export from http://localhost:8000/docs
   - Click "Download OpenAPI spec"
   - Import to Postman

2. Test all endpoints systematically

### Mobile App Testing

```bash
cd mobile

# Run Jest tests (if configured)
npm test

# Type checking
npx tsc --noEmit
```

---

## Part 8: Production Readiness Checks

Before going live:

- [ ] Change all secret keys
- [ ] Use production Stripe keys
- [ ] Set up proper database backups
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Test on multiple devices
- [ ] Perform security audit
- [ ] Load testing completed
- [ ] Error handling tested
- [ ] Edge cases covered

---

## Quick Start Commands Reference

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Mobile:**
```bash
cd mobile
npx expo start
```

**Database:**
```bash
psql -U parkinguser -d parkingspots
```

---

## Getting Help

If you encounter issues:

1. **Check backend logs** - Look for errors in terminal
2. **Check mobile console** - Shake device → "Debug Remote JS"
3. **Check database** - Verify data exists
4. **Check network** - Ensure devices can reach backend
5. **Check documentation** - Review API docs at `/docs`

---

**Last Updated:** February 9, 2026
**Version:** 1.0
