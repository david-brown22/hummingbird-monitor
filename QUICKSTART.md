# 🐦 Hummingbird Monitor - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- Git

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
python setup.py
```

### Option 2: Manual Setup

#### Backend Setup
```bash
# 1. Create virtual environment
cd backend
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Start server
python run_server.py
```

#### Frontend Setup
```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start development server
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Test the Setup

### Test Database
```bash
cd backend
python test_db.py
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Get birds
curl http://localhost:8000/api/birds/
```

## 📱 Using the Application

1. **Dashboard**: View real-time statistics and charts
2. **Birds**: Manage individual bird profiles
3. **Visits**: Track and analyze visit patterns  
4. **Alerts**: Monitor feeder status
5. **Summaries**: View AI-generated reports
6. **Settings**: Configure system preferences

## 🔧 Configuration

### Environment Variables
Copy `backend/env.example` to `backend/.env` and configure:

```bash
# Required
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here

# Optional
CODEPROJECT_AI_URL=http://localhost:32168
BLUE_IRIS_URL=http://your-blue-iris-server:port
```

### Database
- **Default**: SQLite (no setup required)
- **Production**: PostgreSQL (update DATABASE_URL)

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port 8000
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Python dependencies fail**
   ```bash
   # Update pip
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Node.js dependencies fail**
   ```bash
   # Clear cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

### Logs
- **Backend**: Check terminal output
- **Frontend**: Check browser console
- **Database**: Check `backend/hummingbird_monitor.db`

## 📚 Next Steps

1. **Configure AI Services**: Set up OpenAI and Pinecone
2. **Add Camera Integration**: Connect Blue Iris
3. **Test Bird Identification**: Upload test images
4. **Set Up Alerts**: Configure notification thresholds
5. **Generate Summaries**: Test AI summary generation

## 🆘 Need Help?

- **Documentation**: Check README.md
- **Issues**: Create GitHub issue
- **API Docs**: Visit http://localhost:8000/docs
- **Architecture**: See architecture.md

---

**Happy Bird Watching! 🐦✨**
