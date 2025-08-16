# 📦 ApexAgent Installation Guide

**Complete Setup Instructions for All Deployment Scenarios**

## 📋 System Requirements

### Minimum Requirements
- **Operating System:** Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python:** 3.11 or higher
- **Node.js:** 18.0 or higher
- **Memory:** 4GB RAM minimum, 8GB recommended
- **Storage:** 2GB free space minimum, 10GB recommended
- **Network:** Internet connection for AI provider APIs

### Recommended Requirements
- **Operating System:** Latest stable versions
- **Python:** 3.11+ with virtual environment support
- **Node.js:** 20.0+ with npm/yarn
- **Memory:** 16GB RAM for optimal performance
- **Storage:** 50GB+ for development and data
- **Network:** High-speed internet for real-time features

## 🚀 Quick Installation

### Option 1: Automated Setup (Recommended)

1. **Clone Repository**
   ```bash
   git clone https://github.com/AllienNova/APEXAGENT_FRESH.git
   cd APEXAGENT_FRESH
   ```

2. **Run Automated Setup**
   ```bash
   chmod +x deployment/scripts/deploy.sh
   ./deployment/scripts/deploy.sh
   ```

3. **Access Applications**
   - **ApexAgent Core:** http://localhost:3000
   - **Aideon Lite AI:** http://localhost:5000

### Option 2: Manual Installation

#### Step 1: Backend Setup
```bash
# Navigate to backend directory
cd core/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp deployment/environments/development/.env.example .env
# Edit .env with your configuration
```

#### Step 2: Frontend Setup
```bash
# Navigate to frontend directory
cd core/frontend

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

#### Step 3: Aideon Lite AI Setup
```bash
# Navigate to Aideon Lite directory
cd integrations/aideon_lite

# Install dependencies
pip install flask flask-cors requests together huggingface_hub

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in the root directory:
```env
# AI Provider API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
TOGETHER_API_KEY=your_together_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Database Configuration
DATABASE_URL=sqlite:///apexagent.db

# Security Configuration
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Application Configuration
FLASK_ENV=development
DEBUG=True
PORT=5000

# Firebase Configuration (Optional)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
```

### API Key Setup

#### 1. OpenAI API Key
1. Visit https://platform.openai.com/
2. Create account or sign in
3. Navigate to API Keys section
4. Create new API key
5. Copy key to `.env` file

#### 2. Anthropic API Key
1. Visit https://console.anthropic.com/
2. Create account or sign in
3. Navigate to API Keys section
4. Create new API key
5. Copy key to `.env` file

#### 3. Google API Key
1. Visit https://makersuite.google.com/
2. Create account or sign in
3. Create new API key
4. Copy key to `.env` file

#### 4. Together AI API Key
1. Visit https://api.together.xyz/
2. Create account or sign in
3. Navigate to API Keys section
4. Create new API key
5. Copy key to `.env` file

#### 5. Hugging Face API Key
1. Visit https://huggingface.co/settings/tokens
2. Create account or sign in
3. Create new access token
4. Copy token to `.env` file

## 🏃‍♂️ Running the Applications

### Development Mode

#### Terminal 1: Backend
```bash
cd core/backend/src
python main.py
# Backend running at http://localhost:8000
```

#### Terminal 2: Frontend
```bash
cd core/frontend
npm start
# Frontend running at http://localhost:3000
```

#### Terminal 3: Aideon Lite AI
```bash
cd integrations/aideon_lite/src
python main.py
# Aideon Lite running at http://localhost:5000
```

### Production Mode

#### Using Docker
```bash
cd deployment/docker
docker-compose up -d
```

#### Using PM2 (Node.js Process Manager)
```bash
# Install PM2
npm install -g pm2

# Start applications
pm2 start ecosystem.config.js
```

## 🌐 Deployment Options

### 1. Local Development
- **Use Case:** Development and testing
- **Setup Time:** 10-15 minutes
- **Cost:** Free
- **Scalability:** Single user

### 2. Firebase + Vercel
- **Use Case:** Production deployment
- **Setup Time:** 30-45 minutes
- **Cost:** $5-15/month
- **Scalability:** High

### 3. Docker Containers
- **Use Case:** Containerized deployment
- **Setup Time:** 20-30 minutes
- **Cost:** Infrastructure dependent
- **Scalability:** Very high

### 4. Kubernetes
- **Use Case:** Enterprise deployment
- **Setup Time:** 1-2 hours
- **Cost:** Infrastructure dependent
- **Scalability:** Unlimited

## 🔍 Verification

### Health Checks

#### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

#### Frontend Health Check
```bash
curl http://localhost:3000
# Expected: HTML response with React app
```

#### Aideon Lite Health Check
```bash
curl http://localhost:5000/api/dashboard/metrics
# Expected: JSON with system metrics
```

### Functionality Tests

#### 1. AI Provider Test
```bash
# Test OpenAI integration
curl -X POST http://localhost:5000/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!", "provider": "openai"}'
```

#### 2. Authentication Test
```bash
# Test login functionality
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

#### 3. Dashboard Test
- Navigate to http://localhost:5000
- Login with demo/demo123
- Verify all 10 tabs are functional
- Check real-time updates

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :5000
# Kill process
kill -9 <PID>
```

#### 2. Python Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 3. Node.js Dependencies
```bash
# Clear npm cache
npm cache clean --force
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. API Key Issues
- Verify API keys are correctly set in `.env`
- Check API key permissions and quotas
- Test API keys independently

#### 5. Database Issues
```bash
# Reset database
rm apexagent.db
python -c "from app import create_tables; create_tables()"
```

### Performance Issues

#### 1. Slow Response Times
- Check internet connection
- Verify API provider status
- Monitor system resources

#### 2. Memory Usage
- Increase system RAM
- Optimize Python virtual environment
- Use production-grade WSGI server

#### 3. Frontend Loading Issues
- Clear browser cache
- Check browser console for errors
- Verify frontend build process

## 📊 Monitoring

### System Monitoring
- **CPU Usage:** Monitor via system tools
- **Memory Usage:** Check RAM consumption
- **Disk Space:** Ensure adequate storage
- **Network:** Monitor API request rates

### Application Monitoring
- **Response Times:** Track API latency
- **Error Rates:** Monitor failure rates
- **User Activity:** Track usage patterns
- **Security Events:** Monitor threat detection

## 🔄 Updates

### Updating ApexAgent
```bash
# Pull latest changes
git pull origin main

# Update backend dependencies
cd core/backend
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd ../frontend
npm update

# Restart applications
./deployment/scripts/deploy.sh
```

### Version Management
- **Semantic Versioning:** Major.Minor.Patch format
- **Release Notes:** Check GitHub releases
- **Backup:** Always backup before updates
- **Testing:** Test in development first

## 📞 Support

### Getting Help
- **Documentation:** Check `/documentation/` directory
- **GitHub Issues:** Report bugs and request features
- **Community:** Join GitHub Discussions
- **Email:** Contact development team

### Reporting Issues
1. Check existing documentation
2. Search GitHub Issues
3. Provide detailed error information
4. Include system specifications
5. Attach relevant log files

---

**ApexAgent Installation Complete - Welcome to the Future of AI Automation!** 🚀

