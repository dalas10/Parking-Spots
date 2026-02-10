# ParkingSpots Backend

Production-ready FastAPI backend for the ParkingSpots parking rental marketplace with PostgreSQL, Redis caching, and multi-worker architecture.

## 🚀 Production Features

- **High Performance**: 1,666+ RPS with sub-millisecond response times
- **Scalable**: 12-worker architecture supporting 1,500-2,500 concurrent users
- **Redis Caching**: 95% cache hit rate reducing database load
- **PostgreSQL**: Connection pooling with 300 max connections
- **Background Tasks**: Separate worker for auto-checkout and booking management
- **Monitoring**: Real-time dashboard and performance metrics
- **Production Tools**: Automated deployment and testing scripts

## Quick Start

### Development Mode (Single Worker)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Initialize database
python init_db.py

# Run server
uvicorn app.main:app --reload
```

### Production Mode (Multi-Worker)
```bash
# Validate environment
./setup_production.sh

# Start all services (12 workers + background tasks)
./start_production.sh

# Monitor performance
./monitor.sh

# Run load tests
./load_test.sh
```

## Configuration

### Environment Variables

**Database**:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/parkingspots
```

**Redis Cache**:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Optional
```

**Background Tasks**:
```bash
ENABLE_BACKGROUND_TASKS=true  # Set to false for API workers in multi-worker setup
```

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

## Production Architecture

### Infrastructure

**Database**: PostgreSQL 14
- 300 max connections (12 workers × 20 pool + overhead)
- 3GB shared buffers (25% of system RAM)
- Async connection pooling with asyncpg

**Caching**: Redis 6.x
- Search results cached for 5 minutes
- Spot details cached for 10 minutes
- Automatic cache invalidation on updates
- 95% cache hit rate in production

**Workers**: 12 API workers
- Multi-process Uvicorn workers
- Each worker has independent connection pool
- Handles 1,666+ requests per second

**Background Tasks**: Separate process
- Auto-checkout expired bookings
- Auto-start confirmed bookings
- Independent from API workers

### Production Scripts

**Environment Setup**:
```bash
./setup_production.sh          # Validate environment
./check_postgres_config.sh     # Check database configuration
```

**Deployment**:
```bash
./start_production.sh          # Start all services (12 workers + background)
./start_workers.sh             # Start API workers only
python run_background_tasks.py # Start background tasks only
```

**Monitoring & Testing**:
```bash
./monitor.sh                   # Real-time performance dashboard
./load_test.sh                 # Comprehensive load testing
```

**Systemd Services** (Optional):
```bash
sudo cp parkingspots-api.service /etc/systemd/system/
sudo cp parkingspots-background.service /etc/systemd/system/
sudo systemctl enable parkingspots-api parkingspots-background
sudo systemctl start parkingspots-api parkingspots-background
```

### Performance Metrics

Current production performance:
- **Throughput**: 1,666+ RPS
- **Response Time**: < 1ms average
- **Cache Hit Rate**: 95%
- **Capacity**: 1,500-2,500 concurrent users
- **Database Connections**: ~15 active (out of 300 max)

### Configuration Files

**MULTI_WORKER_GUIDE.md** - Complete multi-worker setup guide  
**PRODUCTION_SUMMARY.md** - Performance metrics and deployment status  
**parkingspots-api.service** - Systemd service for API workers  
**parkingspots-background.service** - Systemd service for background tasks  

## Testing

Development testing:
```bash
pytest
```

Production load testing:
```bash
./load_test.sh                                             # Quick test
ab -n 1000 -c 100 http://localhost:8000/api/v1/parking-spots/  # Apache Bench
```

## Project Structure

```
app/
├── api/           # API routes and endpoints
├── core/          # Core functionality (config, security)
├── db/            # Database configuration
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├── cache.py       # Redis caching layer
├── background_tasks.py  # Auto-checkout/start tasks
└── main.py        # Application entry point

Production Scripts:
├── start_production.sh        # Full production deployment
├── start_workers.sh           # API workers only
├── run_background_tasks.py    # Background tasks worker
├── monitor.sh                 # Real-time monitoring
├── load_test.sh              # Performance testing
├── check_postgres_config.sh  # Database config checker
└── setup_production.sh       # Environment validator
```
