# Local APK Build Instructions

## Prerequisites
1. Install Android Studio from https://developer.android.com/studio
2. Install Java Development Kit (JDK) 11 or higher
3. Set up environment variables:
   ```bash
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/emulator
   export PATH=$PATH:$ANDROID_HOME/tools
   export PATH=$PATH:$ANDROID_HOME/tools/bin
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   ```

## Build Steps

1. **Prebuild the native projects:**
   ```bash
   cd /home/dalas/ParkingSpots/mobile
   npx expo prebuild --platform android
   ```

2. **Build the APK:**
   ```bash
   cd android
   ./gradlew assembleRelease
   ```

3. **Find your APK:**
   The APK will be at:
   ```
   android/app/build/outputs/apk/release/app-release.apk
   ```

4. **Transfer to phone:**
   ```bash
   adb install app-release.apk
   ```
   Or transfer the file manually and install.

⚠️ **Note:** Local builds require significant setup. EAS Build is much easier for first-time users.
