# 🔧 Hummingbird Monitor Troubleshooting Guide

This comprehensive troubleshooting guide will help you diagnose and resolve common issues with the Hummingbird Monitor system.

## 🚨 Common Issues

### 1. Installation Issues

#### Python Version Issues
**Problem**: `Python 3.8+ is required`
**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.8+ if needed
# Windows: Download from python.org
# macOS: brew install python@3.8
# Ubuntu: sudo apt install python3.8
```

#### Virtual Environment Issues
**Problem**: `ModuleNotFoundError: No module named 'app'`
**Solution**:
```bash
# Create and activate virtual environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Node.js Issues
**Problem**: `Node.js 16+ is required`
**Solution**:
```bash
# Check Node.js version
node --version

# Install Node.js 16+ if needed
# Windows: Download from nodejs.org
# macOS: brew install node@16
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
```

### 2. Database Issues

#### Database Connection Errors
**Problem**: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError)`
**Solution**:
```bash
# Check database file permissions
ls -la backend/hummingbird_monitor.db

# Recreate database
cd backend
rm hummingbird_monitor.db
python init_db.py
```

#### Migration Issues
**Problem**: `alembic.util.exc.CommandError: Can't locate revision`
**Solution**:
```bash
# Reset database
cd backend
rm hummingbird_monitor.db
python init_db.py

# Or run migrations manually
alembic upgrade head
```

#### Database Lock Issues
**Problem**: `sqlite3.OperationalError: database is locked`
**Solution**:
```bash
# Check for running processes
ps aux | grep python

# Kill stuck processes
pkill -f "python run_server.py"

# Restart database
cd backend
python init_db.py
```

### 3. API Issues

#### Port Already in Use
**Problem**: `Address already in use: Port 8000`
**Solution**:
```bash
# Find process using port 8000
netstat -tulpn | grep :8000
# or
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
python run_server.py --port 8001
```

#### CORS Issues
**Problem**: `CORS error: Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000'`
**Solution**:
```bash
# Check CORS configuration in backend/main.py
# Ensure CORS_ORIGINS includes http://localhost:3000
```

#### API Timeout Issues
**Problem**: `Request timeout after 30 seconds`
**Solution**:
```bash
# Check system resources
top
htop

# Increase timeout in configuration
# Set REQUEST_TIMEOUT=60 in .env file
```

### 4. Frontend Issues

#### Build Failures
**Problem**: `npm run build` fails
**Solution**:
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check for dependency conflicts
npm audit
npm audit fix
```

#### Development Server Issues
**Problem**: `npm start` fails or doesn't start
**Solution**:
```bash
# Check if port 3000 is available
netstat -tulpn | grep :3000

# Use different port
npm start -- --port 3001

# Check for syntax errors
npm run lint
```

#### React Router Issues
**Problem**: `404 Not Found` on page refresh
**Solution**:
```bash
# Check if using HashRouter instead of BrowserRouter
# Update src/App.js to use HashRouter for development
```

### 5. AI Service Issues

#### OpenAI API Issues
**Problem**: `openai.error.AuthenticationError: Invalid API key`
**Solution**:
```bash
# Check API key in .env file
cat backend/.env | grep OPENAI_API_KEY

# Verify API key is valid
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

#### CodeProject.AI Connection Issues
**Problem**: `Connection refused: localhost:32168`
**Solution**:
```bash
# Check if CodeProject.AI is running
curl http://localhost:32168/status

# Start CodeProject.AI if not running
# Download and install from codeproject.com

# Check firewall settings
sudo ufw status
```

#### Vector Database Issues
**Problem**: `pinecone.exceptions.PineconeException: Invalid API key`
**Solution**:
```bash
# Check Pinecone configuration
cat backend/.env | grep PINECONE

# Verify Pinecone API key
# Create new index if needed
# Use FAISS as fallback for local development
```

### 6. Blue Iris Integration Issues

#### Webhook Not Working
**Problem**: Blue Iris webhooks not reaching the API
**Solution**:
```bash
# Check webhook URL in Blue Iris
# Ensure URL is correct: http://your-server:8000/api/captures/webhook/blue-iris

# Test webhook manually
curl -X POST http://localhost:8000/api/captures/webhook/blue-iris \
  -H "Content-Type: application/json" \
  -d '{"camera": "test", "trigger": "motion"}'

# Check Blue Iris web server settings
```

#### Camera Connection Issues
**Problem**: Cameras not detected or not working
**Solution**:
```bash
# Check camera network connectivity
ping <camera_ip>

# Verify camera credentials in Blue Iris
# Check camera settings and permissions
# Test camera feed in Blue Iris interface
```

### 7. Performance Issues

#### High Memory Usage
**Problem**: System using too much memory
**Solution**:
```bash
# Check memory usage
free -h
htop

# Optimize Python memory usage
# Set PYTHONHASHSEED=0
# Use memory profiling tools
```

#### Slow Database Queries
**Problem**: Database queries taking too long
**Solution**:
```bash
# Check database indexes
sqlite3 backend/hummingbird_monitor.db ".indexes"

# Create missing indexes
python -c "
from app.core.database import engine
engine.execute('CREATE INDEX IF NOT EXISTS idx_visits_bird_id ON visits(bird_id)')
engine.execute('CREATE INDEX IF NOT EXISTS idx_visits_feeder_id ON visits(feeder_id)')
engine.execute('CREATE INDEX IF NOT EXISTS idx_visits_visit_time ON visits(visit_time)')
"
```

#### Slow AI Processing
**Problem**: Bird identification taking too long
**Solution**:
```bash
# Check CodeProject.AI performance
curl http://localhost:32168/status

# Optimize image processing
# Reduce image resolution
# Use GPU acceleration if available
```

### 8. Logging Issues

#### Log Files Not Created
**Problem**: No log files in logs/ directory
**Solution**:
```bash
# Create logs directory
mkdir -p backend/logs

# Check file permissions
chmod 755 backend/logs

# Verify logging configuration
python -c "import logging; print(logging.getLogger().handlers)"
```

#### Log Files Too Large
**Problem**: Log files consuming too much disk space
**Solution**:
```bash
# Check log file sizes
du -h backend/logs/

# Rotate log files
logrotate -f /etc/logrotate.d/hummingbird-monitor

# Clean old logs
find backend/logs/ -name "*.log.*" -mtime +30 -delete
```

### 9. Network Issues

#### Firewall Issues
**Problem**: API not accessible from external networks
**Solution**:
```bash
# Check firewall status
sudo ufw status

# Allow necessary ports
sudo ufw allow 8000
sudo ufw allow 3000

# Configure firewall rules
sudo ufw enable
```

#### DNS Issues
**Problem**: Cannot resolve hostnames
**Solution**:
```bash
# Check DNS configuration
cat /etc/resolv.conf

# Test DNS resolution
nslookup google.com

# Use IP addresses instead of hostnames
```

### 10. Security Issues

#### SSL Certificate Issues
**Problem**: SSL certificate errors
**Solution**:
```bash
# Check certificate validity
openssl x509 -in certificate.crt -text -noout

# Renew certificate
certbot renew

# Test SSL configuration
openssl s_client -connect yourdomain.com:443
```

#### Authentication Issues
**Problem**: API authentication failing
**Solution**:
```bash
# Check authentication configuration
cat backend/.env | grep SECRET_KEY

# Verify JWT token format
# Check token expiration
# Validate user credentials
```

## 🔍 Diagnostic Tools

### System Health Check
```bash
# Check system resources
htop
free -h
df -h

# Check network connectivity
ping google.com
curl -I http://localhost:8000/health

# Check process status
ps aux | grep python
ps aux | grep node
```

### Database Health Check
```bash
# Check database file
ls -la backend/hummingbird_monitor.db

# Test database connection
python -c "
from app.core.database import engine
result = engine.execute('SELECT 1').fetchone()
print('Database connection:', result)
"

# Check database integrity
sqlite3 backend/hummingbird_monitor.db "PRAGMA integrity_check;"
```

### API Health Check
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/observability/health
curl http://localhost:8000/api/birds

# Check API documentation
curl http://localhost:8000/docs
```

### Frontend Health Check
```bash
# Test frontend
curl http://localhost:3000
curl http://localhost:3000/static/js/bundle.js

# Check build process
cd frontend
npm run build
```

## 📊 Performance Monitoring

### System Metrics
```bash
# Monitor system performance
top
htop
iotop
nethogs

# Check disk usage
df -h
du -h backend/logs/

# Monitor network
netstat -tulpn
ss -tulpn
```

### Application Metrics
```bash
# Check API metrics
curl http://localhost:8000/api/observability/metrics

# Check performance data
curl http://localhost:8000/api/observability/performance

# Check logs
tail -f backend/logs/hummingbird_monitor.log
```

### Database Performance
```bash
# Check database performance
sqlite3 backend/hummingbird_monitor.db ".timer on"
sqlite3 backend/hummingbird_monitor.db "EXPLAIN QUERY PLAN SELECT * FROM visits WHERE bird_id = 1;"

# Analyze database
sqlite3 backend/hummingbird_monitor.db "ANALYZE;"
```

## 🛠️ Maintenance Tasks

### Regular Maintenance
```bash
# Clean old logs
find backend/logs/ -name "*.log.*" -mtime +30 -delete

# Optimize database
sqlite3 backend/hummingbird_monitor.db "VACUUM;"
sqlite3 backend/hummingbird_monitor.db "ANALYZE;"

# Update dependencies
cd backend && pip install -r requirements.txt --upgrade
cd frontend && npm update
```

### Backup Procedures
```bash
# Backup database
cp backend/hummingbird_monitor.db backend/backup_$(date +%Y%m%d).db

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz backend/.env frontend/.env

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz backend/logs/
```

### Recovery Procedures
```bash
# Restore database
cp backend/backup_20240115.db backend/hummingbird_monitor.db

# Restore configuration
tar -xzf config_backup_20240115.tar.gz

# Restart services
cd backend && python run_server.py &
cd frontend && npm start &
```

## 📞 Getting Help

### Before Asking for Help
1. **Check the logs** for error messages
2. **Review the documentation** for configuration details
3. **Search GitHub issues** for similar problems
4. **Test with minimal configuration** to isolate issues

### When Reporting Issues
Include the following information:
- **Operating system** and version
- **Python and Node.js versions**
- **Error messages** and logs
- **Configuration details** (without sensitive information)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**

### Support Channels
- **GitHub Issues**: [Create an issue](https://github.com/david-brown22/hummingbird-monitor/issues)
- **Discord Community**: [Join our Discord](https://discord.gg/hummingbird-monitor)
- **Stack Overflow**: [Ask a question](https://stackoverflow.com/questions/tagged/hummingbird-monitor)

### Useful Commands
```bash
# Get system information
uname -a
python --version
node --version
npm --version

# Check service status
systemctl status hummingbird-monitor
journalctl -u hummingbird-monitor

# Monitor logs
tail -f backend/logs/hummingbird_monitor.log
tail -f backend/logs/errors.log
```

This troubleshooting guide should help you resolve most common issues with the Hummingbird Monitor system. For additional help, refer to the support channels or create an issue on GitHub.
