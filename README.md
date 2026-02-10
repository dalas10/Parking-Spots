# ParkingSpots 🅿️

A full-stack parking space rental marketplace where property owners can list their parking spots and users can search, book, and pay for parking through a mobile app.

## Features

### For Renters (Users looking for parking)
- 🗺️ **Location-based search** - Find parking spots near you with map view
- 📅 **Easy booking** - Book spots with flexible hourly, daily, or monthly rates
- 💳 **Secure payments** - Pay through Stripe integration
- ⭐ **Reviews & ratings** - Read and leave reviews for parking spots
- 📱 **Real-time availability** - See which spots are currently available
- 🔔 **Booking management** - Track active and past bookings

### For Owners (Property owners with parking)
- 📝 **List parking spots** - Upload details, photos, and set pricing
- 💰 **Earnings dashboard** - Track income and payouts
- 📊 **Manage bookings** - Confirm, track, and manage reservations
- 💬 **Respond to reviews** - Engage with customer feedback
- ⏰ **Set availability** - Control when your spot is available

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with async SQLAlchemy
- **Authentication**: JWT with refresh tokens
- **Payments**: Stripe Connect
- **Real-time**: WebSockets/Redis

### Mobile App
- **Framework**: React Native with Expo
- **State Management**: Zustand
- **Navigation**: React Navigation
- **Maps**: React Native Maps
- **Payments**: Stripe React Native SDK

## Project Structure

```
ParkingSpots/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── users.py
│   │   │       │   ├── parking_spots.py
│   │   │       │   ├── bookings.py
│   │   │       │   ├── reviews.py
│   │   │       │   └── payments.py
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── parking_spot.py
│   │   │   ├── booking.py
│   │   │   ├── review.py
│   │   │   └── payment.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── parking_spot.py
│   │   │   ├── booking.py
│   │   │   ├── review.py
│   │   │   └── payment.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
│
└── mobile/
    ├── src/
    │   ├── components/
    │   ├── navigation/
    │   ├── screens/
    │   │   ├── auth/
    │   │   ├── home/
    │   │   ├── parking/
    │   │   ├── bookings/
    │   │   └── profile/
    │   ├── services/
    │   ├── stores/
    │   ├── types/
    │   └── utils/
    ├── App.tsx
    ├── app.json
    └── package.json
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (for real-time features)
- Stripe account

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb parkingspots
   
   # Tables are created automatically on startup
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access API docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Mobile App Setup

1. **Navigate to mobile directory**
   ```bash
   cd mobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API URL**
   - Update `src/services/api.ts` with your backend URL

4. **Start the app**
   ```bash
   npm start
   # Then press 'a' for Android or 'i' for iOS
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/change-password` - Change password

### Parking Spots
- `GET /api/v1/parking-spots` - Search/list parking spots
- `POST /api/v1/parking-spots` - Create new listing
- `GET /api/v1/parking-spots/{id}` - Get spot details
- `PUT /api/v1/parking-spots/{id}` - Update listing
- `DELETE /api/v1/parking-spots/{id}` - Delete listing
- `GET /api/v1/parking-spots/my-spots` - Get owner's listings

### Bookings
- `POST /api/v1/bookings/calculate-price` - Calculate booking price
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings` - Get user's bookings
- `GET /api/v1/bookings/owner` - Get owner's received bookings
- `PUT /api/v1/bookings/{id}/status` - Update booking status
- `POST /api/v1/bookings/{id}/check-in` - Check in
- `POST /api/v1/bookings/{id}/check-out` - Check out

### Reviews
- `POST /api/v1/reviews` - Create review
- `GET /api/v1/reviews/spot/{id}` - Get spot reviews
- `GET /api/v1/reviews/spot/{id}/summary` - Get review summary
- `POST /api/v1/reviews/{id}/response` - Owner response

### Payments
- `POST /api/v1/payments/create-payment-intent` - Create Stripe payment
- `POST /api/v1/payments/confirm-payment` - Confirm payment
- `POST /api/v1/payments/refund` - Request refund
- `GET /api/v1/payments/owner/summary` - Get payout summary

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/parkingspots
SECRET_KEY=your-super-secret-key
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
REDIS_URL=redis://localhost:6379
```

## Database Schema

### Core Models
- **User** - User accounts with authentication
- **ParkingSpot** - Parking spot listings
- **Booking** - Reservations linking users to spots
- **Review** - User reviews for spots
- **Payment** - Payment records
- **Payout** - Owner payouts

## Deployment

### Backend (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Mobile App
```bash
# Build for production
eas build --platform all

# Submit to stores
eas submit
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
