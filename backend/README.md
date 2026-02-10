# ParkingSpots Backend

FastAPI backend for the ParkingSpots parking rental marketplace.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run server
uvicorn app.main:app --reload
```

## Configuration

### Payment Processing

The app supports optional payment processing via Stripe. You can configure this behavior using the `SKIP_PAYMENT_PROCESSING` environment variable:

**Development/Testing Mode** (default):
```bash
SKIP_PAYMENT_PROCESSING=true
```
- Bookings are automatically confirmed without payment
- Status: `CONFIRMED`, Payment status: `completed`
- Ideal for testing the app without Stripe integration

**Production Mode** (with real Stripe):
```bash
SKIP_PAYMENT_PROCESSING=false
STRIPE_SECRET_KEY=sk_live_your_real_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_real_key
STRIPE_WEBHOOK_SECRET=whsec_your_real_secret
```
- Bookings require payment confirmation
- Status: `PENDING` → `CONFIRMED` after payment
- Payment status: `pending` → `completed` after payment
- Full payment flow with Stripe integration

### Booking Management

The system includes comprehensive booking management features:

**Time-Based Availability:**
- Search endpoint filters out spots with active bookings
- Pass `start_time` and `end_time` parameters to see only available spots
- Works seamlessly with existing filters (city, type, price, etc.)

**Double-Booking Prevention:**
- Automatic validation prevents conflicting reservations
- Checks PENDING, CONFIRMED, and IN_PROGRESS bookings
- Returns 409 Conflict error if time slot is already booked

**Checkout System:**
- Manual checkout: `POST /api/v1/bookings/{id}/check-out`
- Auto-checkout when booking time expires (runs every minute)
- Auto-start bookings at their scheduled start time
- Updates parking spot statistics on completion

**Booking Lifecycle:**
```
PENDING → CONFIRMED → IN_PROGRESS → COMPLETED
              ↓             ↓
          CANCELLED    CANCELLED
```

The background service automatically:
1. Starts bookings (CONFIRMED → IN_PROGRESS) at their start time
2. Completes bookings (IN_PROGRESS/CONFIRMED → COMPLETED) after their end time

## API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations

Using Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

```bash
pytest
```

## Project Structure

```
app/
├── api/           # API routes and endpoints
├── core/          # Core functionality (config, security)
├── db/            # Database configuration
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
└── main.py        # Application entry point
```
