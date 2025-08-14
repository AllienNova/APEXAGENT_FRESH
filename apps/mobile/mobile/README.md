# Aideon Lite AI - Mobile Application

A powerful React Native mobile application that provides full access to the Aideon Lite AI system's capabilities on iOS and Android devices.

## 🚀 Features

### Core AI Capabilities
- **Multi-Model Chat Interface** - Access to 30+ AI models (GPT-4o, Claude 3.5, Gemini 2.0, Llama 3.3, etc.)
- **Real-time Dashboard** - System health, usage metrics, and activity monitoring
- **File Management** - Upload, process, and manage documents with AI analysis
- **Voice Integration** - Voice-to-text and text-to-speech capabilities
- **Offline Support** - Core functionality available without internet connection

### Mobile-Optimized Features
- **Biometric Authentication** - Fingerprint and Face ID security
- **Push Notifications** - Real-time alerts and system updates
- **Camera Integration** - Document scanning and image analysis
- **Background Processing** - Continue AI tasks when app is minimized
- **Cross-Device Sync** - Seamless synchronization with web and desktop versions

## 📱 Platform Support

- **iOS**: 13.0 and above
- **Android**: API level 21 (Android 5.0) and above
- **React Native**: 0.72.7

## 🛠 Development Setup

### Prerequisites

```bash
# Install Node.js (16 or higher)
node --version  # Should be 16+

# Install React Native CLI
npm install -g react-native-cli

# For iOS development (macOS only)
# Install Xcode from App Store
# Install CocoaPods
sudo gem install cocoapods

# For Android development
# Install Android Studio
# Set up Android SDK and emulator
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AllienNova/ApexAgent.git
cd ApexAgent/mobile
```

2. **Install dependencies**
```bash
npm install

# For iOS (macOS only)
cd ios && pod install && cd ..
```

3. **Configure environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# API_BASE_URL=https://api.aideonlite.com
# ENVIRONMENT=development
```

### Running the Application

#### iOS Development
```bash
# Start Metro bundler
npm start

# Run on iOS simulator
npm run ios

# Run on specific iOS device
npm run ios -- --device "iPhone 14 Pro"
```

#### Android Development
```bash
# Start Metro bundler
npm start

# Run on Android emulator/device
npm run android

# Run on specific Android device
npm run android -- --deviceId=<device_id>
```

## 🏗 Project Structure

```
mobile/
├── src/
│   ├── screens/              # App screens
│   │   ├── ChatScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   ├── ProjectsScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── services/             # Business logic
│   │   ├── auth.service.ts
│   │   ├── api.service.ts
│   │   ├── notifications.ts
│   │   └── offline.ts
│   ├── components/           # Reusable components
│   │   ├── common/
│   │   ├── chat/
│   │   └── dashboard/
│   ├── navigation/           # Navigation setup
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── TabNavigator.tsx
│   ├── store/               # Redux store
│   │   ├── slices/
│   │   ├── middleware/
│   │   └── index.ts
│   └── utils/               # Utilities
│       ├── constants.ts
│       ├── helpers.ts
│       └── types.ts
├── android/                 # Android-specific code
├── ios/                     # iOS-specific code
├── package.json
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the mobile directory:

```env
# API Configuration
API_BASE_URL=https://api.aideonlite.com
API_TIMEOUT=30000

# Environment
ENVIRONMENT=development

# Features
ENABLE_BIOMETRIC_AUTH=true
ENABLE_PUSH_NOTIFICATIONS=true
ENABLE_OFFLINE_MODE=true

# Analytics
ENABLE_ANALYTICS=true
ANALYTICS_KEY=your_analytics_key

# Debugging
ENABLE_FLIPPER=true
LOG_LEVEL=debug
```

### Firebase Configuration

1. **iOS Setup**
   - Download `GoogleService-Info.plist` from Firebase Console
   - Add to `ios/AideonLiteMobile/GoogleService-Info.plist`

2. **Android Setup**
   - Download `google-services.json` from Firebase Console
   - Add to `android/app/google-services.json`

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### E2E Tests
```bash
# Install Detox (iOS)
npm install -g detox-cli

# Build and test iOS
detox build --configuration ios.sim.debug
detox test --configuration ios.sim.debug

# Build and test Android
detox build --configuration android.emu.debug
detox test --configuration android.emu.debug
```

## 📦 Building for Production

### iOS Production Build
```bash
# Clean and build
npm run clean
cd ios && pod install && cd ..

# Build archive
npm run build:ios

# Or use Xcode
# Open ios/AideonLiteMobile.xcworkspace in Xcode
# Product > Archive
```

### Android Production Build
```bash
# Clean and build
npm run clean

# Generate signed APK
npm run build:android

# Generate AAB for Play Store
cd android
./gradlew bundleRelease
```

## 🔐 Security Features

### Authentication
- **Biometric Authentication** - Fingerprint/Face ID
- **JWT Token Management** - Secure token storage
- **Auto-logout** - Session timeout protection
- **PIN/Pattern Backup** - Alternative authentication methods

### Data Protection
- **Keychain Storage** - Secure credential storage
- **Certificate Pinning** - API communication security
- **Data Encryption** - Local data encryption
- **Privacy Controls** - Granular permission management

## 📊 Performance Optimization

### Bundle Size Optimization
- **Code Splitting** - Dynamic imports for large features
- **Tree Shaking** - Remove unused code
- **Image Optimization** - WebP format and compression
- **Bundle Analysis** - Regular size monitoring

### Runtime Performance
- **Lazy Loading** - Load screens on demand
- **Memory Management** - Proper cleanup and disposal
- **Background Tasks** - Efficient background processing
- **Caching Strategy** - Smart data caching

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/mobile.yml
name: Mobile CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd mobile && npm install
      - name: Run tests
        run: cd mobile && npm test
      - name: Build Android
        run: cd mobile && npm run build:android
```

## 📱 App Store Deployment

### iOS App Store
1. **Prepare for submission**
   - Update version in `ios/AideonLiteMobile/Info.plist`
   - Create app screenshots and metadata
   - Test on physical devices

2. **Submit via Xcode**
   - Archive the app
   - Upload to App Store Connect
   - Fill out app information
   - Submit for review

### Google Play Store
1. **Prepare for submission**
   - Update version in `android/app/build.gradle`
   - Generate signed AAB
   - Create store listing assets

2. **Submit via Play Console**
   - Upload AAB file
   - Fill out store listing
   - Set up pricing and distribution
   - Submit for review

## 🐛 Troubleshooting

### Common Issues

**Metro bundler issues**
```bash
npm start -- --reset-cache
```

**iOS build issues**
```bash
cd ios && pod install && cd ..
npm run ios
```

**Android build issues**
```bash
cd android && ./gradlew clean && cd ..
npm run android
```

**Network issues**
```bash
# Check API connectivity
curl -X GET https://api.aideonlite.com/health
```

## 📞 Support

- **Documentation**: [docs.aideonlite.com](https://docs.aideonlite.com)
- **Issues**: [GitHub Issues](https://github.com/AllienNova/ApexAgent/issues)
- **Discord**: [Community Chat](https://discord.gg/aideonlite)
- **Email**: support@aideonlite.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with ❤️ by the Aideon Lite AI Team**

