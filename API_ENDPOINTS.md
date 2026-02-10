# ParkingSpots API Endpoints

**Base URL:** `http://localhost:8000/api/v1`

**Interactive Documentation:** http://localhost:8000/docs

---

## Authentication Endpoints

### Register New User
- **POST** `/api/v1/auth/register`
- **Description:** Create a new user account
- **Auth:** None required
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "phone_number": "+1234567890"
  }
  ```

### Login
- **POST** `/api/v1/auth/login`
- **Description:** Login and get access token
- **Auth:** None required
- **Body:** `application/x-www-form-urlencoded`
  ```
  username=user@example.com
  password=SecurePass123!
  ```

### Refresh Token
- **POST** `/api/v1/auth/refresh`
- **Description:** Get new access token using refresh token
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "refresh_token": "your_refresh_token"
  }
  ```

### Forgot Password
- **POST** `/api/v1/auth/forgot-password`
- **Description:** Request password reset
- **Auth:** None required
- **Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```

---

## User Endpoints

### Get Current User Profile
- **GET** `/api/v1/users/me`
- **Description:** Get authenticated user's profile
- **Auth:** Bearer token required

### Update Current User Profile
- **PUT** `/api/v1/users/me`
- **Description:** Update user profile
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "full_name": "John Smith",
    "phone_number": "+1234567890",
    "profile_image": "https://..."
  }
  ```

### Change Password
- **POST** `/api/v1/users/me/change-password`
- **Description:** Change user password
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "current_password": "OldPass123!",
    "new_password": "NewPass123!"
  }
  ```

### Get User By ID
- **GET** `/api/v1/users/{user_id}`
- **Description:** Get public user profile
- **Auth:** Bearer token required

### Delete Account
- **DELETE** `/api/v1/users/me`
- **Description:** Delete user account
- **Auth:** Bearer token required

---

## Parking Spot Endpoints

### Create Parking Spot
- **POST** `/api/v1/parking-spots`
- **Description:** Create new parking spot listing
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "title": "Downtown Covered Parking",
    "description": "Safe covered parking near metro",
    "address": "123 Main St, City",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "price_per_hour": 5.00,
    "price_per_day": 40.00,
    "price_per_month": 800.00,
    "spot_type": "covered",
    "vehicle_size": "standard",
    "amenities": ["covered", "ev_charging", "security"],
    "images": ["https://..."]
  }
  ```

### Search Parking Spots
- **GET** `/api/v1/parking-spots`
- **Description:** Search parking spots with filters
- **Auth:** Bearer token required
- **Query Parameters:**
  - `latitude` - Location latitude
  - `longitude` - Location longitude
  - `radius` - Search radius in km (default: 5)
  - `min_price` - Minimum price per hour
  - `max_price` - Maximum price per hour
  - `spot_type` - Filter by type (covered, garage, etc.)
  - `vehicle_size` - Required vehicle size
  - `start_time` - Availability start time (ISO 8601)
  - `end_time` - Availability end time (ISO 8601)
  - `amenities` - Comma-separated amenities

### Get My Parking Spots
- **GET** `/api/v1/parking-spots/my-spots`
- **Description:** Get all parking spots owned by current user
- **Auth:** Bearer token required

### Get Parking Spot Details
- **GET** `/api/v1/parking-spots/{spot_id}`
- **Description:** Get detailed information about a parking spot
- **Auth:** Bearer token required

### Update Parking Spot
- **PUT** `/api/v1/parking-spots/{spot_id}`
- **Description:** Update parking spot details
- **Auth:** Bearer token required (must be owner)
- **Body:** Same as create, all fields optional

### Delete Parking Spot
- **DELETE** `/api/v1/parking-spots/{spot_id}`
- **Description:** Delete a parking spot
- **Auth:** Bearer token required (must be owner)

### Add Availability Slot
- **POST** `/api/v1/parking-spots/{spot_id}/availability`
- **Description:** Add availability time slot
- **Auth:** Bearer token required (must be owner)
- **Body:**
  ```json
  {
    "start_time": "2026-02-10T09:00:00Z",
    "end_time": "2026-02-10T18:00:00Z",
    "is_recurring": false,
    "recurring_pattern": null
  }
  ```

### Get Availability Slots
- **GET** `/api/v1/parking-spots/{spot_id}/availability`
- **Description:** Get all availability slots for a spot
- **Auth:** Bearer token required

### Delete Availability Slot
- **DELETE** `/api/v1/parking-spots/{spot_id}/availability/{slot_id}`
- **Description:** Remove an availability slot
- **Auth:** Bearer token required (must be owner)

---

## Booking Endpoints

### Calculate Booking Price
- **POST** `/api/v1/bookings/calculate-price`
- **Description:** Calculate total price for a booking
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "spot_id": "uuid",
    "start_time": "2026-02-10T09:00:00Z",
    "end_time": "2026-02-10T17:00:00Z"
  }
  ```

### Create Booking
- **POST** `/api/v1/bookings`
- **Description:** Create new parking booking
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "spot_id": "uuid",
    "start_time": "2026-02-10T09:00:00Z",
    "end_time": "2026-02-10T17:00:00Z",
    "vehicle_plate": "ABC123",
    "notes": "Blue Honda Civic"
  }
  ```

### Get My Bookings
- **GET** `/api/v1/bookings`
- **Description:** Get all bookings for current user
- **Auth:** Bearer token required
- **Query Parameters:**
  - `status` - Filter by status (pending, confirmed, active, completed, cancelled)
  - `upcoming` - Only show upcoming bookings (true/false)

### Get Owner Bookings
- **GET** `/api/v1/bookings/owner`
- **Description:** Get all bookings for owner's parking spots
- **Auth:** Bearer token required
- **Query Parameters:**
  - `spot_id` - Filter by specific spot
  - `status` - Filter by status

### Get Booking Details
- **GET** `/api/v1/bookings/{booking_id}`
- **Description:** Get detailed booking information
- **Auth:** Bearer token required

### Update Booking Status
- **PUT** `/api/v1/bookings/{booking_id}/status`
- **Description:** Update booking status (owner only)
- **Auth:** Bearer token required (must be spot owner)
- **Body:**
  ```json
  {
    "status": "confirmed",
    "notes": "Approved"
  }
  ```

### Check In
- **POST** `/api/v1/bookings/{booking_id}/check-in`
- **Description:** Mark booking as checked in
- **Auth:** Bearer token required

### Check Out
- **POST** `/api/v1/bookings/{booking_id}/check-out`
- **Description:** Mark booking as checked out
- **Auth:** Bearer token required

---

## Payment Endpoints

### Create Payment Intent
- **POST** `/api/v1/payments/create-payment-intent`
- **Description:** Create Stripe payment intent for booking
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "booking_id": "uuid",
    "payment_method_id": "pm_card_visa"
  }
  ```

### Confirm Payment
- **POST** `/api/v1/payments/confirm-payment`
- **Description:** Confirm payment completion
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "payment_intent_id": "pi_xxx",
    "booking_id": "uuid"
  }
  ```

### Stripe Webhook
- **POST** `/api/v1/payments/webhook`
- **Description:** Stripe webhook endpoint for payment events
- **Auth:** Stripe signature verification

### Request Refund
- **POST** `/api/v1/payments/refund`
- **Description:** Request refund for a booking
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "booking_id": "uuid",
    "reason": "Cancellation due to emergency"
  }
  ```

### Get My Payments
- **GET** `/api/v1/payments/my-payments`
- **Description:** Get all payments made by user
- **Auth:** Bearer token required

### Get Owner Payouts
- **GET** `/api/v1/payments/owner/payouts`
- **Description:** Get payout history for owner
- **Auth:** Bearer token required

### Get Payout Summary
- **GET** `/api/v1/payments/owner/summary`
- **Description:** Get earnings summary for owner
- **Auth:** Bearer token required
- **Response:**
  ```json
  {
    "total_earnings": 1250.00,
    "pending_payouts": 350.00,
    "completed_payouts": 900.00,
    "total_bookings": 25
  }
  ```

### Create Stripe Connect Account
- **POST** `/api/v1/payments/connect/create-account`
- **Description:** Create Stripe Connect account for receiving payouts
- **Auth:** Bearer token required

---

## Review Endpoints

### Create Review
- **POST** `/api/v1/reviews`
- **Description:** Leave a review for a parking spot
- **Auth:** Bearer token required
- **Body:**
  ```json
  {
    "spot_id": "uuid",
    "booking_id": "uuid",
    "rating": 5,
    "comment": "Great parking spot, very convenient!",
    "cleanliness_rating": 5,
    "security_rating": 5,
    "accessibility_rating": 4
  }
  ```

### Get Spot Reviews
- **GET** `/api/v1/reviews/spot/{spot_id}`
- **Description:** Get all reviews for a parking spot
- **Auth:** Bearer token required
- **Query Parameters:**
  - `limit` - Max number of reviews
  - `offset` - Pagination offset

### Get Review Summary
- **GET** `/api/v1/reviews/spot/{spot_id}/summary`
- **Description:** Get review statistics for a spot
- **Auth:** Bearer token required
- **Response:**
  ```json
  {
    "average_rating": 4.5,
    "total_reviews": 24,
    "rating_distribution": {
      "5": 15,
      "4": 6,
      "3": 2,
      "2": 1,
      "1": 0
    }
  }
  ```

### Get Review Details
- **GET** `/api/v1/reviews/{review_id}`
- **Description:** Get detailed review information
- **Auth:** Bearer token required

### Update Review
- **PUT** `/api/v1/reviews/{review_id}`
- **Description:** Update own review
- **Auth:** Bearer token required (must be reviewer)
- **Body:** Same as create, all fields optional

### Add Owner Response
- **POST** `/api/v1/reviews/{review_id}/response`
- **Description:** Add owner response to a review
- **Auth:** Bearer token required (must be spot owner)
- **Body:**
  ```json
  {
    "response": "Thank you for the feedback!"
  }
  ```

### Mark Review Helpful
- **POST** `/api/v1/reviews/{review_id}/helpful`
- **Description:** Mark a review as helpful
- **Auth:** Bearer token required

### Delete Review
- **DELETE** `/api/v1/reviews/{review_id}`
- **Description:** Delete own review
- **Auth:** Bearer token required (must be reviewer)

---

## Response Status Codes

- **200 OK** - Request succeeded
- **201 Created** - Resource created successfully
- **204 No Content** - Success with no response body
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation error
- **500 Internal Server Error** - Server error

---

## Authentication

Most endpoints require authentication using Bearer tokens:

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

To get a token:
1. Register: `POST /api/v1/auth/register`
2. Login: `POST /api/v1/auth/login`
3. Use the returned `access_token` in subsequent requests

---

## Testing with cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "phone_number": "+1234567890"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123!"
```

**Get Profile:**
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Interactive API Documentation

Visit **http://localhost:8000/docs** for:
- ✅ Interactive API testing
- ✅ Complete request/response schemas
- ✅ Try out endpoints directly
- ✅ Authentication support

---

**Total Endpoints: 50+**

Last Updated: February 9, 2026
