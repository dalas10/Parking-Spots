# Urbee Mobile App Setup

## Features Added ✨
- ✅ Enhanced multi-field search (title, address, city, zip)
- ✅ Date/time availability filtering
- ✅ City-based search
- ✅ Spot type filters
- ✅ EV charging and covered parking filters
- ✅ Urbee Gold branding throughout
- ✅ Network API support (connects to backend at 192.168.53.100:8000)

## Installation

### 1. Install Dependencies
```bash
cd mobile
npm install
```

### 2. Start the App

**For Android:**
```bash
npm start
# Then press 'a' for Android emulator
# OR scan QR code with Expo Go app on your phone
```

**For iOS:**
```bash
npm start
# Then press 'i' for iOS simulator
# OR scan QR code with Expo Go app on your iPhone
```

### 3. Testing Features

1. **Search**: Tap the search bar on the home screen
2. **Filters**: 
   - Enter text to search by location/address
   - Select city from dropdown
   - Choose parking type
   - Toggle date/time availability filtering
   - Enable EV charging or covered parking filters
3. **View Results**: See parking spots on map and list view
4. **Book**: Tap any spot to see details and book

## API Configuration

The app automatically connects to:
- **Development**: http://192.168.53.100:8000/api/v1
- **Production**: https://api.parkingspots.com/api/v1

Make sure the backend is running on your local network!

## Build for Production

### Android APK
```bash
# Using EAS Build (Expo Application Services)
npm install -g eas-cli
eas build --platform android --profile preview

# Traditional method
npm run android -- --variant=release
```

### iOS
```bash
eas build --platform ios
```

## New Screens
- **SearchScreen** - Full filter interface matching web app

## Updated Features
- Multi-field text search across parking spots
- Date/time availability checking
- Urbee Gold color scheme (#FDB82E)
- Improved UX with proper filtering

## Color Scheme
- Primary: #FDB82E (Urbee Gold)
- Success: #27AE60
- Error: #EF4444
- Text: #2C3E50

Enjoy your fully-featured mobile parking app! 🚗🅿️
