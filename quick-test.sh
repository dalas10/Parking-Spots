#!/bin/bash

# ParkingSpots Quick Test Script
# This script helps you quickly verify the backend is working

echo "🅿️  ParkingSpots - Quick Backend Test"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo -e "${YELLOW}Start it with: cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}"
    exit 1
fi

echo ""
echo "2. Testing API endpoints..."

# Test user registration
echo -n "   - User registration... "
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "quicktest'$(date +%s)'@example.com",
    "password": "TestPass123!",
    "full_name": "Quick Test",
    "phone_number": "+1234567890"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    echo -e "${GREEN}✓${NC}"
    
    # Extract email for login
    TEST_EMAIL=$(echo "$REGISTER_RESPONSE" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
    
    # Test login
    echo -n "   - User login... "
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=$TEST_EMAIL&password=TestPass123!")
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo -e "${GREEN}✓${NC}"
        
        # Extract token
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        
        # Test authenticated endpoint
        echo -n "   - Get user profile... "
        PROFILE_RESPONSE=$(curl -s http://localhost:8000/api/v1/users/me \
          -H "Authorization: Bearer $TOKEN")
        
        if echo "$PROFILE_RESPONSE" | grep -q "$TEST_EMAIL"; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    else
        echo -e "${RED}✗${NC}"
    fi
else
    echo -e "${RED}✗${NC}"
    echo "   Response: $REGISTER_RESPONSE"
fi

echo ""
echo "3. API Documentation:"
echo "   📚 Visit: http://localhost:8000/docs"
echo ""
echo -e "${GREEN}======================================"
echo "✓ Quick test complete!"
echo -e "======================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:8000/docs in your browser"
echo "  2. Start the mobile app: cd mobile && npx expo start"
echo "  3. Read TESTING_GUIDE.md for complete testing instructions"
echo ""
