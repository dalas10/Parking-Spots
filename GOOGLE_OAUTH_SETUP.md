# Google OAuth Setup Guide

## Overview
The ParkingSpots application now supports Google Sign-In/Sign-Up, allowing users to authenticate using their Google accounts.

## Backend Configuration

### 1. Database Changes
The `users` table has been updated with OAuth support:
- `oauth_provider` - Stores the OAuth provider name ('google', 'facebook', etc.)
- `oauth_id` - Stores the unique ID from the OAuth provider
- `hashed_password` - Now nullable (OAuth users don't have passwords)

### 2. Environment Variables
Add to `/backend/.env`:
```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

### 3. API Endpoints
New endpoints added:
- `POST /api/v1/oauth/google` - Authenticate/register with Google
- `GET /api/v1/oauth/google/config` - Get OAuth configuration

## Setting Up Google OAuth

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name it "ParkingSpots" or similar

### Step 2: Enable Google+ API
1. Navigate to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click "Enable"

### Step 3: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Add authorized JavaScript origins:
   ```
   http://localhost:3000
   http://localhost:8000
   ```
5. Add authorized redirect URIs:
   ```
   http://localhost:3000/auth/google/callback
   http://localhost:3000
   ```
6. Click "Create"
7. Copy the **Client ID** and **Client Secret**

### Step 4: Configure Application
1. Open `/backend/.env`
2. Replace placeholders with your credentials:
   ```env
   GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=YOUR_ACTUAL_CLIENT_SECRET
   ```
3. Save the file

### Step 5: Update Frontend
1. Open `/web/login.html`
2. Find line with `client_id:`
3. Replace the placeholder with your Client ID:
   ```javascript
   client_id: 'YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com',
   ```
4. Do the same for `/web/register.html`

### Step 6: Restart Backend
```bash
cd /home/dalas/ParkingSpots/backend
source venv/bin/activate
# Kill existing server
pkill -f "uvicorn"
# Restart with new config
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## How It Works

### User Flow

#### Sign In
1. User clicks "Sign in with Google" button
2. Google OAuth popup appears
3. User selects/authorizes Google account
4. Google returns ID token to frontend
5. Frontend sends token to `/api/v1/oauth/google`
6. Backend verifies token with Google
7. Backend finds or creates user account
8. Backend returns JWT tokens
9. User is logged in

#### Sign Up
Same flow as Sign In, but user can select role (renter/owner) before authentication.

### Backend Process
1. **Token Verification**: Verify Google ID token using `google.oauth2.id_token`
2. **Extract User Data**: Get email, name, picture from token
3. **Find/Create User**:
   - If user exists (by email or oauth_id): Log them in
   - If new user: Create account with Google data
4. **Set OAuth Fields**:
   - `oauth_provider = 'google'`
   - `oauth_id = <Google user ID>`
   - `is_verified = True` (Google verifies emails)
5. **Return Tokens**: Generate and return JWT access/refresh tokens

### Security Features
- ✅ Token verification with Google servers
- ✅ Issuer validation (accounts.google.com only)
- ✅ Email verification included
- ✅ No password storage for OAuth users
- ✅ Existing user detection (prevents duplicates)

## Frontend Integration

### Login Page (`login.html`)
- Google Sign-In button above email/password form
- "OR" divider for visual separation
- Automatic login on successful OAuth

### Register Page (`register.html`)
- Google Sign-Up button at top
- Role selection preserved (renter/owner)
- Skips email verification (Google pre-verified)

### Translations
Supported in both English and Greek:
- "OR" → "Ή"
- "Sign in with Google" → "Σύνδεση με Google"
- "Sign up with Google" → "Εγγραφή με Google"

## Testing

### Test Google Sign-In
1. Open http://localhost:3000/login.html
2. Click the Google Sign-In button
3. Authorize with your Google account
4. Should redirect to home page logged in
5. Check browser console for any errors
6. Verify token stored in localStorage

### Verify Backend
```bash
# Check if OAuth endpoint is registered
curl http://localhost:8000/api/v1/oauth/google/config

# Should return:
# {"client_id":"your-client-id.apps.googleusercontent.com","redirect_uri":"http://localhost:3000/auth/google/callback"}
```

### Test Database
```bash
cd /home/dalas/ParkingSpots/backend
sqlite3 parkingspots.db "SELECT email, full_name, oauth_provider, oauth_id, is_verified FROM users WHERE oauth_provider = 'google';"
```

## Troubleshooting

### "Invalid Google token" Error
- **Cause**: Wrong Client ID or token expired
- **Fix**: Verify GOOGLE_CLIENT_ID in .env matches Google Console

### "Wrong issuer" Error
- **Cause**: Token not from Google
- **Fix**: Regenerate token, check Google SDK loaded correctly

### Button Not Appearing
- **Cause**: Google SDK not loaded
- **Fix**: Check browser console, verify internet connection
- **Check**: `<script src="https://accounts.google.com/gsi/client" async defer></script>`

### User Already Exists
- **Cause**: Email already registered with password
- **Fix**: Working as intended - OAuth links to existing account

### Database Schema Errors
- **Cause**: Missing columns (oauth_provider, oauth_id)
- **Fix**: Restart backend to auto-create columns

## Production Considerations

### Domain Configuration
1. Update authorized origins in Google Console:
   ```
   https://yourproductiondomain.com
   ```

2. Update authorized redirect URIs:
   ```
   https://yourproductiondomain.com/auth/google/callback
   ```

3. Update .env:
   ```env
   GOOGLE_REDIRECT_URI=https://yourproductiondomain.com/auth/google/callback
   ```

### Security
- ✅ Use HTTPS in production
- ✅ Restrict Client ID to production domain
- ✅ Keep Client Secret secure (never commit to git)
- ✅ Rate limit OAuth endpoints
- ✅ Monitor for abuse

### User Privacy
- Only request necessary scopes (email, profile)
- Display privacy policy on sign-up
- Allow users to disconnect Google account
- Comply with GDPR/privacy laws

## Features

✅ **Implemented:**
- Google Sign-In on login page
- Google Sign-Up on register page
- Backend OAuth verification
- User creation/linking
- JWT token generation
- Multi-language support
- Profile picture sync

⏳ **Future Enhancements:**
- Facebook OAuth
- Apple Sign-In
- Link/unlink OAuth accounts
- Multiple OAuth providers per user
- OAuth account management page

## API Documentation

### POST /api/v1/oauth/google
Authenticate or register user with Google.

**Request Body:**
```json
{
  "token": "google-id-token-string",
  "role": "renter"  // or "owner", optional
}
```

**Response:**
```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "full_name": "John Doe",
    "role": "renter",
    "profile_image": "https://...",
    "is_verified": true
  }
}
```

**Error Responses:**
- `401` - Invalid token
- `400` - Token verification failed
- `500` - Server error

### GET /api/v1/oauth/google/config
Get Google OAuth configuration.

**Response:**
```json
{
  "client_id": "your-client-id.apps.googleusercontent.com",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}
```

## Support
For issues with Google OAuth:
1. Check Google Cloud Console for quota limits
2. Verify credentials are correct
3. Check browser console for errors
4. Review backend logs
5. Test with different Google account
