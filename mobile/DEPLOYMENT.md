# Radio Recorder Mobile App - Deployment Guide

This guide provides step-by-step instructions for building, testing, and deploying the Radio Recorder mobile app to iOS App Store and Google Play Store.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [App Store Deployment](#app-store-deployment-ios)
3. [Google Play Deployment](#google-play-deployment-android)
4. [Build Instructions](#build-instructions)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Version Management](#version-management)

## Prerequisites

### Required Software

- Node.js 18+ and npm 9+
- Xcode 14+ (for iOS)
- Android Studio 2022+ (for Android)
- Java JDK 11+ (for Android)
- Capacitor CLI 5.6.0+
- Git

### Development Accounts

- [Apple Developer Account](https://developer.apple.com) ($99/year)
- [Google Play Console Account](https://play.google.com/console) ($25 one-time)

### Certificates and Keys

Create a directory to store sensitive files:

```bash
mkdir -p ~/.radio-recorder-keys
chmod 700 ~/.radio-recorder-keys
```

**Important:** Never commit keys, certificates, or credentials to git!

## App Store Deployment (iOS)

### 1. Generate App Store Connect Credentials

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Create a new app:
   - Name: "Radio Recorder"
   - Primary Language: English
   - Bundle ID: `com.radiorecorder.app`
   - SKU: `radio-recorder-001`
   - Category: Music

### 2. Create Signing Certificates

1. Open Xcode:
   ```bash
   xcode-select --install
   ```

2. Create Signing Certificate:
   - Open Xcode → Preferences → Accounts
   - Click "Manage Certificates"
   - Click "+" → "iOS Development" → Create
   - Or go to [Certificates, IDs & Profiles](https://developer.apple.com/account/resources/certificates/list)

3. Create Provisioning Profile:
   - Certificates, Identifiers & Profiles → Identifiers
   - Create new identifier for App ID: `com.radiorecorder.app`
   - Create Provisioning Profile:
     - Type: "App Store"
     - App ID: `com.radiorecorder.app`
     - Certificate: Select your certificate
     - Devices: Not applicable for App Store
     - Profile name: `RadioRecorder-AppStore`

### 3. Configure Xcode Project

```bash
cd mobile
npm run build
npx cap sync ios
npx cap open ios
```

In Xcode:

1. Select "App" project in navigator
2. Select "App" target
3. Go to "Signing & Capabilities" tab:
   - Team: Select your team
   - Bundle Identifier: `com.radiorecorder.app`
   - Signing Certificate: Automatic
   - Provisioning Profile: Automatic

4. Configure App Settings:
   - Display Name: "Radio Recorder"
   - Version: `1.0.0`
   - Build: `1`
   - Deployment Target: iOS 14.0 minimum

### 4. Build for App Store

```bash
# In Xcode
Product → Scheme → App
Product → Destination → Generic iOS Device
Product → Build

# Or from command line
xcodebuild -workspace ios/App/App.xcworkspace \
  -scheme App \
  -configuration Release \
  -derivedDataPath build
```

### 5. Create App Store Archive

In Xcode:
- Product → Archive
- Validate App (check for errors)
- Distribute App → App Store Connect

Follow the prompts to upload to App Store Connect.

### 6. Submit for Review

In App Store Connect:

1. Build → Select uploaded build
2. TestFlight → Add build to TestFlight for internal testing first
3. App Information:
   - Screenshots (required for each device size)
   - App Preview Video (optional)
   - Description, Keywords, Support URL, Privacy Policy
4. Pricing & Availability:
   - Price Tier: Free
   - Regions: Select all
5. Review Information:
   - Contact information
   - Demo account (if needed)
6. Click "Submit for Review"

**Review typically takes 24-48 hours**

### 7. TestFlight Internal Testing

Before submitting to App Store, test with TestFlight:

```bash
# In App Store Connect
TestFlight → Internal Testing → Add testers
# Invite team members or account holders
```

## Google Play Deployment (Android)

### 1. Create Google Play Console Account

1. Go to [Google Play Console](https://play.google.com/console)
2. Pay $25 one-time developer fee
3. Create new app:
   - App name: "Radio Recorder"
   - Default language: English
   - App or game: App
   - Free or paid: Free

### 2. Generate Signing Key

```bash
# Generate keystore file
keytool -genkey -v -keystore \
  ~/.radio-recorder-keys/radio-recorder-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias radio-recorder-key

# When prompted, enter:
# Keystore password: [secure password]
# Key password: [same or different]
# Fill in your information
```

**Important:** Save the passwords securely. You'll need them for future builds.

### 3. Configure Android Signing

Create `android/local.properties`:

```properties
sdk.dir=/path/to/Android/sdk
flutter.sdk=/path/to/flutter

# Signing configuration
STORE_FILE=/Users/yourname/.radio-recorder-keys/radio-recorder-release.jks
STORE_PASSWORD=your_keystore_password
KEY_ALIAS=radio-recorder-key
KEY_PASSWORD=your_key_password
```

**Never commit this file to git!**

### 4. Configure Gradle Build

The `android/app/build.gradle` already includes signing configuration.
Just ensure the signing block references the local.properties:

```gradle
signingConfigs {
    release {
        storeFile file(STORE_FILE)
        storePassword STORE_PASSWORD
        keyAlias KEY_ALIAS
        keyPassword KEY_PASSWORD
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled true
    }
}
```

### 5. Build Release APK and AAB

```bash
cd mobile

# Build AAB (recommended for Google Play)
npm run build
npx cap sync android

cd android
./gradlew bundleRelease
# Output: android/app/build/outputs/bundle/release/app-release.aab

# Or build APK for testing
./gradlew assembleRelease
# Output: android/app/build/outputs/apk/release/app-release.apk
```

### 6. Upload to Google Play Console

1. Go to Google Play Console → Your app
2. Release → Production
3. Click "Create new release"
4. Upload `app-release.aab` file
5. Fill in release notes (required)
6. Review app content (required):
   - Content rating
   - Target audience
   - Permissions review
7. Click "Review release"
8. Click "Rollout to production"

**Your app will be available within 2-3 hours**

## Build Instructions

### Development Build

```bash
cd mobile

# Web development
npm run dev

# iOS simulator
npm run ios

# Android emulator
npm run android
```

### Production Build

```bash
cd mobile

# Web production
npm run build

# iOS release
npm run build:ios

# Android release
npm run build:android
```

### Using Build Scripts

#### Unix/Mac

```bash
# Web build
./scripts/build.sh web

# iOS build
./scripts/build.sh ios production

# Android build
./scripts/build.sh android production
```

#### Windows

```batch
# Web build
scripts\build.bat web

# iOS build
scripts\build.bat ios production

# Android build
scripts\build.bat android production
```

## Testing

### Unit Tests

```bash
# Create test directory
mkdir -p src/__tests__

# Run tests (configure with vitest or jest)
npm test
```

### Manual Testing

1. **Radio Player Testing**
   - Select different stations
   - Test play/pause/resume/stop
   - Test volume control
   - Test bitrate selection
   - Test ad skip toggle

2. **Recording Testing**
   - Start/stop/pause/resume recording
   - Verify file size and duration
   - Test different bitrates

3. **Dashboard Testing**
   - View analytics
   - Check transcription results
   - Review playback history

4. **Settings Testing**
   - Toggle preferences
   - Change API URL
   - Verify dark mode

5. **Device Testing**
   - Test on actual iOS and Android devices
   - Test on various screen sizes
   - Test with slow network connection
   - Test offline mode

### Performance Testing

Use Chrome DevTools for Android and Safari for iOS:

```bash
# Android
# 1. Connect device via USB
# 2. Enable USB debugging
# 3. Open chrome://inspect in Chrome
# 4. Click "Inspect" on your app

# iOS
# 1. Connect device via USB
# 2. Open Safari → Develop → [Device] → [App]
```

## Troubleshooting

### Common Issues

#### Xcode Build Fails

```bash
# Clean Xcode cache
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Reinstall pods
cd ios/App
pod install --repo-update
```

#### Gradle Build Fails

```bash
# Clean Gradle cache
cd android
./gradlew clean

# Update Gradle
./gradlew wrapper --gradle-version latest
```

#### Capacitor Sync Issues

```bash
# Full sync
npx cap sync

# iOS specific
npx cap sync ios
rm -rf ios/App/Pods
cd ios/App && pod install --repo-update && cd ../../

# Android specific
npx cap sync android
./android/gradlew -p android clean
```

#### API Connection Issues

Check `.env.production`:

```bash
# Verify API URL
cat .env.production

# Test connection
curl -X GET https://api.radiorecorder.com/health
```

## Version Management

### Updating Version Numbers

1. **package.json**
   ```json
   {
     "version": "1.0.1"
   }
   ```

2. **iOS (capacitor.config.ts)**
   ```typescript
   {
     appId: 'com.radiorecorder.app',
     appName: 'Radio Recorder',
     version: '1.0.1'
   }
   ```

3. **Android (capacitor.config.ts & build.gradle)**
   ```typescript
   // Same version in capacitor.config.ts
   ```

   ```gradle
   android {
     compileSdkVersion 33
     defaultConfig {
       versionCode 2  // Increment this
       versionName "1.0.1"
     }
   }
   ```

### Release Checklist

- [ ] Update version numbers in all files
- [ ] Update CHANGELOG.md with new features/fixes
- [ ] Run full test suite
- [ ] Test on iOS simulator and device
- [ ] Test on Android emulator and device
- [ ] Build production APK/AAB
- [ ] Test production build locally
- [ ] Create git tag: `git tag v1.0.1`
- [ ] Build for App Store
- [ ] Build for Google Play
- [ ] Submit to App Store Review
- [ ] Submit to Google Play
- [ ] Announce release on social media

## CI/CD Pipeline

The project includes GitHub Actions workflows that automate builds:

- `.github/workflows/build-ios.yml` - Automatic iOS build on push
- `.github/workflows/build-android.yml` - Automatic Android build on push

### Required GitHub Secrets

Set these in your GitHub repository settings:

**iOS:**
- `XCODE_TEAM_ID` - Apple Team ID
- `XCODE_TEAM_NAME` - Apple Team Name
- `XCODE_PROJECT` - Path to xcworkspace (e.g., `mobile/ios/App/App.xcworkspace`)

**Android:**
- `ANDROID_SIGNING_KEY` - Base64-encoded keystore file
- `ANDROID_SIGNING_KEY_ALIAS` - Keystore alias
- `ANDROID_SIGNING_STORE_PASSWORD` - Keystore password
- `ANDROID_SIGNING_KEY_PASSWORD` - Key password
- `PLAY_STORE_SERVICE_ACCOUNT_JSON` - Google Play service account JSON

To encode keystore as Base64:

```bash
base64 ~/.radio-recorder-keys/radio-recorder-release.jks | tr -d '\n'
```

## Support and Troubleshooting

For issues or questions:

1. Check the main [README.md](./README.md)
2. Check the [SETUP.md](./SETUP.md)
3. Review [Capacitor Documentation](https://capacitorjs.com/docs)
4. Check GitHub Issues in the project repository
5. Contact the development team

## Legal

- Apple App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Google Play Console Help: https://support.google.com/googleplay/android-developer/
- Privacy Policy Template: https://www.termly.io/
- Terms of Service Template: https://www.termly.io/
