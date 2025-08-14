# Aideon Lite AI - Software Development Kits (SDKs)

This directory contains client SDKs for integrating Aideon Lite AI capabilities into third-party applications across multiple programming languages and platforms.

## 🚀 Available SDKs

### JavaScript/TypeScript SDK
**Location:** `javascript/`  
**Package:** `@aideon/lite-sdk`  
**Platform:** NPM Registry  

```javascript
import { AideonClient } from '@aideon/lite-sdk';

const client = new AideonClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.aideonlite.com'
});

const response = await client.chat.send({
  message: 'Hello, Aideon!',
  model: 'gpt-4o'
});
```

### Python SDK
**Location:** `python/`  
**Package:** `aideon-lite-sdk`  
**Platform:** PyPI  

```python
from aideon_lite_sdk import AideonClient

client = AideonClient(
    api_key='your-api-key',
    base_url='https://api.aideonlite.com'
)

response = client.chat.send(
    message='Hello, Aideon!',
    model='claude-3-5-sonnet'
)
```

### Swift SDK
**Location:** `swift/`  
**Package:** `AideonLiteSDK`  
**Platform:** Swift Package Manager  

```swift
import AideonLiteSDK

let client = AideonClient(
    apiKey: "your-api-key",
    baseURL: "https://api.aideonlite.com"
)

let response = try await client.chat.send(
    message: "Hello, Aideon!",
    model: "gemini-2-0-flash"
)
```

### Android SDK
**Location:** `android/`  
**Package:** `com.aideon:lite-sdk`  
**Platform:** Maven Central / Gradle  

```kotlin
import com.aideon.lite.AideonClient

val client = AideonClient.Builder()
    .apiKey("your-api-key")
    .baseUrl("https://api.aideonlite.com")
    .build()

val response = client.chat().send(
    message = "Hello, Aideon!",
    model = "llama-3-3-70b"
)
```

## 🛠 SDK Features

### Core Capabilities
- **Multi-Model Chat** - Access to 30+ AI models
- **File Processing** - Document analysis and generation
- **Agent Orchestration** - Multi-agent workflows
- **Real-time Streaming** - Live response streaming
- **Authentication** - Secure API key management

### Advanced Features
- **Offline Caching** - Local response caching
- **Rate Limiting** - Built-in request throttling
- **Error Handling** - Comprehensive error management
- **Retry Logic** - Automatic retry with exponential backoff
- **Metrics Collection** - Usage analytics and monitoring

## 📚 Documentation

Each SDK includes:
- **Quick Start Guide** - Get up and running in 5 minutes
- **API Reference** - Complete method documentation
- **Code Examples** - Real-world usage patterns
- **Best Practices** - Performance and security guidelines
- **Migration Guides** - Upgrade instructions between versions

## 🔧 Development

### Building SDKs
```bash
# Build all SDKs
make build-sdks

# Build specific SDK
make build-sdk-javascript
make build-sdk-python
make build-sdk-swift
make build-sdk-android
```

### Testing SDKs
```bash
# Test all SDKs
make test-sdks

# Test specific SDK
make test-sdk-javascript
make test-sdk-python
```

### Publishing SDKs
```bash
# Publish all SDKs
make publish-sdks

# Publish specific SDK
make publish-sdk-javascript
make publish-sdk-python
```

## 📦 Package Information

| SDK | Package Name | Registry | Current Version |
|-----|--------------|----------|-----------------|
| JavaScript | `@aideon/lite-sdk` | NPM | 1.0.0 |
| Python | `aideon-lite-sdk` | PyPI | 1.0.0 |
| Swift | `AideonLiteSDK` | SPM | 1.0.0 |
| Android | `com.aideon:lite-sdk` | Maven | 1.0.0 |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch for the specific SDK
3. Follow the SDK-specific coding standards
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## 📞 Support

- **Documentation**: [docs.aideonlite.com/sdks](https://docs.aideonlite.com/sdks)
- **Issues**: [GitHub Issues](https://github.com/AllienNova/ApexAgent/issues)
- **Discord**: [Developer Community](https://discord.gg/aideonlite-dev)
- **Email**: sdk-support@aideonlite.com

---

**Empowering developers to build AI-powered applications with ease** 🚀

