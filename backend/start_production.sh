#!/bin/bash
# Production startup script with multi-worker API and separate background tasks

set -e

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Configuration
WORKERS=12
API_PORT=8000
API_HOST="0.0.0.0"

echo "🚀 Starting ParkingSpots Production Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        wait $API_PID 2>/dev/null || true
    fi
    if [ ! -z "$BACKGROUND_PID" ]; then
        kill $BACKGROUND_PID 2>/dev/null || true
        wait $BACKGROUND_PID 2>/dev/null || true
    fi
    echo "✅ Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start background tasks worker
echo "1️⃣ Starting background tasks worker..."
ENABLE_BACKGROUND_TASKS=false python run_background_tasks.py &
BACKGROUND_PID=$!
echo "   ✓ Background tasks worker started (PID: $BACKGROUND_PID)"

sleep 2

# Start API with multiple workers
echo "2️⃣ Starting API server with $WORKERS workers..."
ENABLE_BACKGROUND_TASKS=false uvicorn app.main:app \
    --host $API_HOST \
    --port $API_PORT \
    --workers $WORKERS \
    --log-level info \
    --proxy-headers \
    --forwarded-allow-ips='*' &
API_PID=$!
echo "   ✓ API server started (PID: $API_PID)"

echo ""
echo "✅ All services running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 API: http://$API_HOST:$API_PORT"
echo "👷 Workers: $WORKERS"
echo "🔄 Background: Running separately"
echo ""
echo "Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Wait for any process to exit
wait -n

# If we get here, one process died, so cleanup
cleanup
