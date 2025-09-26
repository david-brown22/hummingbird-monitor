# 🚀 Hummingbird Monitor Setup Guide

This comprehensive guide will walk you through setting up the Hummingbird Monitor system from scratch.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Git**: For version control
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 10GB free space minimum

### External Services
- **OpenAI API Key**: For AI summary generation
- **CodeProject.AI**: For computer vision (optional)
- **Blue Iris**: For camera integration (optional)
- **Pinecone Account**: For vector database (optional)

## 🔧 Installation Methods

### Method 1: Automated Setup (Recommended)

The easiest way to get started is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/david-brown22/hummingbird-monitor.git
cd hummingbird-monitor

# Run the automated setup
python setup.py
```

The automated setup will:
- Create virtual environments
- Install all dependencies
- Initialize the database
- Set up configuration files
- Start the services

### Method 2: Manual Setup

If you prefer manual control or the automated setup fails, follow these steps:

## 🐍 Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./hummingbird_monitor.db

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
CODEPROJECT_AI_URL=http://localhost:32168

# Vector Database (Optional)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=hummingbird-embeddings

# Blue Iris Integration (Optional)
BLUE_IRIS_URL=http://your_blue_iris_server:port
BLUE_IRIS_USERNAME=your_username
BLUE_IRIS_PASSWORD=your_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/hummingbird_monitor.log

# Security
SECRET_KEY=your_secret_key_here
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Test Database

```bash
python test_db.py
```

### 6. Start Backend Server

```bash
python run_server.py
```

The backend will be available at `http://localhost:8000`

## ⚛️ Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
```

### 3. Start Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 🔧 Service Configuration

### Blue Iris Integration

#### 1. Install Blue Iris
- Download from [Blue Iris website](https://blueirissoftware.com/)
- Install and configure your cameras
- Enable web server in Blue Iris settings

#### 2. Configure Webhooks
- Go to Blue Iris Settings → Web Server
- Enable web server
- Set webhook URL: `http://your_server:8000/api/captures/webhook/blue-iris`
- Configure motion detection settings

#### 3. Camera Setup
- Position cameras for optimal bird viewing
- Configure motion detection zones
- Set appropriate sensitivity levels
- Test motion detection

### CodeProject.AI Integration

#### 1. Install CodeProject.AI
- Download from [CodeProject.AI website](https://www.codeproject.com/Articles/5322557/CodeProject-AI-Server)
- Install and start the service
- Default URL: `http://localhost:32168`

#### 2. Configure AI Models
- Install required AI models
- Configure model settings
- Test AI inference

#### 3. API Integration
- Verify API connectivity
- Test bird detection
- Configure confidence thresholds

### Pinecone Vector Database

#### 1. Create Pinecone Account
- Sign up at [Pinecone](https://www.pinecone.io/)
- Create a new project
- Generate API key

#### 2. Configure Vector Database
- Set up Pinecone index
- Configure embedding dimensions
- Test vector operations

#### 3. Alternative: FAISS
If you prefer local vector storage:
- FAISS will be used automatically
- No additional configuration needed
- Suitable for development and small deployments

## 🧪 Testing the Installation

### 1. Backend Tests

```bash
cd backend
python test_db.py
python test_capture.py
python test_identification.py
python test_visit_tracking.py
python test_summary_generation.py
python test_feeder_alerts.py
python test_observability.py
```

### 2. Frontend Tests

```bash
cd frontend
npm test
```

### 3. Integration Tests

```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/observability/health

# Test frontend
curl http://localhost:3000
```

## 📊 Monitoring Setup

### 1. Log Configuration

The system automatically creates log files in the `logs/` directory:
- `hummingbird_monitor.log`: Main application log
- `errors.log`: Error log
- `debug.log`: Debug log
- `performance.log`: Performance log

### 2. Metrics Collection

Access system metrics at:
- `http://localhost:8000/api/observability/metrics`
- `http://localhost:8000/api/observability/health`
- `http://localhost:8000/api/observability/dashboard`

### 3. Health Monitoring

Set up health checks:
- Database connectivity
- AI service availability
- Camera system status
- Alert system functionality

## 🔒 Security Configuration

### 1. API Security

```env
# Generate secret key
SECRET_KEY=your_secure_secret_key_here

# Enable CORS for frontend
CORS_ORIGINS=http://localhost:3000
```

### 2. Database Security

```env
# Use strong database credentials
DATABASE_URL=postgresql://username:password@localhost/hummingbird_monitor

# Enable SSL for production
DATABASE_SSL=true
```

### 3. Network Security

- Configure firewall rules
- Use HTTPS in production
- Implement API rate limiting
- Set up authentication

## 🚀 Production Deployment

### 1. Environment Variables

Create production environment file:

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://user:pass@db:5432/hummingbird_monitor

# Security
SECRET_KEY=production_secret_key
CORS_ORIGINS=https://yourdomain.com

# AI Services
OPENAI_API_KEY=your_production_key
CODEPROJECT_AI_URL=http://ai-server:32168
```

### 2. Database Setup

```bash
# Create production database
createdb hummingbird_monitor

# Run migrations
python init_db.py
```

### 3. Web Server Configuration

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL Configuration

```bash
# Install SSL certificate
certbot --nginx -d yourdomain.com
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database status
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').fetchone())"
```

#### 2. AI Service Connection Issues
```bash
# Test CodeProject.AI connection
curl http://localhost:32168/status
```

#### 3. Frontend Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
```

### Log Analysis

#### 1. Check Application Logs
```bash
tail -f logs/hummingbird_monitor.log
```

#### 2. Check Error Logs
```bash
tail -f logs/errors.log
```

#### 3. Check Performance Logs
```bash
tail -f logs/performance.log
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_visits_bird_id ON visits(bird_id);
CREATE INDEX idx_visits_feeder_id ON visits(feeder_id);
CREATE INDEX idx_visits_visit_time ON visits(visit_time);
```

#### 2. API Optimization
- Enable response caching
- Implement request rate limiting
- Use connection pooling
- Optimize database queries

#### 3. Frontend Optimization
- Enable code splitting
- Implement lazy loading
- Use CDN for static assets
- Optimize bundle size

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LangChain Documentation](https://python.langchain.com/)

### Community Support
- [GitHub Issues](https://github.com/david-brown22/hummingbird-monitor/issues)
- [Discord Community](https://discord.gg/hummingbird-monitor)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/hummingbird-monitor)

### Video Tutorials
- [Setup Walkthrough](https://youtube.com/watch?v=setup-tutorial)
- [Configuration Guide](https://youtube.com/watch?v=config-tutorial)
- [Troubleshooting Guide](https://youtube.com/watch?v=troubleshooting-tutorial)

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Review the documentation** for configuration details
3. **Search GitHub issues** for similar problems
4. **Create a new issue** with detailed information
5. **Join the community** for real-time help

### Support Information

When requesting help, please include:
- Operating system and version
- Python and Node.js versions
- Error messages and logs
- Configuration details
- Steps to reproduce the issue

This comprehensive setup guide should get you up and running with the Hummingbird Monitor system. For additional help, refer to the troubleshooting section or reach out to the community.
