#!/bin/bash
# Production startup script with multiple workers

# Activate virtual environment
source venv/bin/activate

# Number of workers = (2 × CPU cores) + 1
# With 20 cores: 8-16 workers recommended
# Using 12 workers for production balance
WORKERS=12

# Start Uvicorn with multiple workers
echo "🚀 Starting ParkingSpots API with $WORKERS workers..."
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $WORKERS \
    --log-level info \
    --access-log
