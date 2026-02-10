# ParkingSpots Mobile App

React Native mobile app for the ParkingSpots parking rental marketplace.

## Quick Start

```bash
# Install dependencies
npm install

# Start Expo development server
npm start
```

## Development

- Press `a` to open on Android emulator
- Press `i` to open on iOS simulator
- Scan QR code with Expo Go app on physical device

## Configuration

Update API URL in `src/services/api.ts`:
```typescript
const API_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1'  // Development
  : 'https://api.parkingspots.com/api/v1';  // Production
```

## Build

```bash
# Development build
npx expo prebuild

# Production build
eas build --platform all
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── navigation/     # React Navigation setup
├── screens/        # Screen components
├── services/       # API services
├── stores/         # Zustand state stores
├── types/          # TypeScript types
└── utils/          # Utility functions
```
