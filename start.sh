#!/bin/bash

# ParkingSpots Quick Start Guide
# Run this script to start the entire system

clear
echo "═══════════════════════════════════════════════"
echo "  🅿️  ParkingSpots - Quick Start"
echo "═══════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if backend is already running
echo -e "${BLUE}[1/3] Checking Backend Status...${NC}"
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is already running!${NC}"
    echo "  → API: http://localhost:8000"
    echo "  → Docs: http://localhost:8000/docs"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}! Backend is not running${NC}"
    BACKEND_RUNNING=false
fi

echo ""

# Check database
echo -e "${BLUE}[2/3] Checking Database...${NC}"
if [ -f "backend/parkingspots.db" ]; then
    USER_COUNT=$(sqlite3 backend/parkingspots.db "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    SPOT_COUNT=$(sqlite3 backend/parkingspots.db "SELECT COUNT(*) FROM parking_spots;" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ Database exists${NC}"
    echo "  → Users: $USER_COUNT"
    echo "  → Parking Spots: $SPOT_COUNT"
else
    echo -e "${RED}✗ Database not found${NC}"
fi

echo ""

# Check mobile dependencies
echo -e "${BLUE}[3/3] Checking Mobile App...${NC}"
if [ -d "mobile/node_modules" ]; then
    echo -e "${GREEN}✓ Mobile dependencies installed${NC}"
else
    echo -e "${YELLOW}! Mobile dependencies not installed${NC}"
    echo "  → Run: cd mobile && npm install"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo ""

# Provide instructions based on status
if [ "$BACKEND_RUNNING" = true ]; then
    echo -e "${GREEN}✓ System is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test API: Open http://localhost:8000/docs"
    echo "  2. Register a user and try the endpoints"
    echo "  3. Start mobile app (see below)"
    echo ""
else
    echo -e "${YELLOW}To start the backend:${NC}"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
fi

echo -e "${BLUE}To start the mobile app:${NC}"
echo "  cd mobile"
echo "  npm install  # (first time only)"
echo "  npx expo start"
echo ""

echo "═══════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "  → API Endpoints: API_ENDPOINTS.md"
echo "  → Testing Guide: TESTING_GUIDE.md"
echo "  → Project Status: PROJECT_STATUS.md"
echo ""
echo "═══════════════════════════════════════════════"
