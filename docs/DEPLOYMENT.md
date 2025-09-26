# 🚀 Hummingbird Monitor Deployment Guide

This guide covers deploying the Hummingbird Monitor system in various environments, from development to production.

## 🏗️ Deployment Architecture

### Production Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server   │    │   Database     │
│   (Nginx)       │───▶│   (FastAPI)    │───▶│   (PostgreSQL) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   AI Services   │    │   File Storage  │
│   (Static)      │    │   (CodeProject) │    │   (Images)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🐳 Docker Deployment

### 1. Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: hummingbird_monitor
      POSTGRES_USER: hummingbird
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  # Backend API
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://hummingbird:secure_password@postgres:5432/hummingbird_monitor
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./backend/logs:/app/logs
      - ./backend/uploads:/app/uploads

  # Frontend
  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2. Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run_server.py"]
```

### 3. Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static {
            alias /usr/share/nginx/html/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 5. Environment Variables

Create `.env`:

```env
# Database
DATABASE_URL=postgresql://hummingbird:secure_password@postgres:5432/hummingbird_monitor

# Redis
REDIS_URL=redis://redis:6379

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
CODEPROJECT_AI_URL=http://localhost:32168

# Security
SECRET_KEY=your_very_secure_secret_key_here

# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### 6. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Instance type: t3.medium or larger
# Security groups: Allow HTTP (80), HTTPS (443), SSH (22)

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. RDS Database Setup

```bash
# Create RDS PostgreSQL instance
# Engine: PostgreSQL 15
# Instance class: db.t3.micro
# Storage: 20GB
# Security group: Allow access from EC2 instance

# Get connection details
# Endpoint: your-db-instance.region.rds.amazonaws.com
# Port: 5432
# Database: hummingbird_monitor
# Username: hummingbird
# Password: secure_password
```

#### 3. Application Deployment

```bash
# Clone repository
git clone https://github.com/david-brown22/hummingbird-monitor.git
cd hummingbird-monitor

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Deploy with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

#### 4. SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Google Cloud Platform

#### 1. Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/hummingbird-backend', './backend']
  
  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/hummingbird-frontend', './frontend']
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/hummingbird-backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/hummingbird-frontend']

images:
  - 'gcr.io/$PROJECT_ID/hummingbird-backend'
  - 'gcr.io/$PROJECT_ID/hummingbird-frontend'
```

#### 2. Deploy to Cloud Run

```bash
# Build and push images
gcloud builds submit --config cloudbuild.yaml

# Deploy backend
gcloud run deploy hummingbird-backend \
  --image gcr.io/$PROJECT_ID/hummingbird-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy hummingbird-frontend \
  --image gcr.io/$PROJECT_ID/hummingbird-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### 1. Azure Container Instances

```bash
# Create resource group
az group create --name hummingbird-rg --location eastus

# Create container registry
az acr create --resource-group hummingbird-rg --name hummingbirdregistry --sku Basic

# Build and push images
az acr build --registry hummingbirdregistry --image hummingbird-backend ./backend
az acr build --registry hummingbirdregistry --image hummingbird-frontend ./frontend

# Deploy containers
az container create \
  --resource-group hummingbird-rg \
  --name hummingbird-backend \
  --image hummingbirdregistry.azurecr.io/hummingbird-backend \
  --ports 8000 \
  --environment-variables DATABASE_URL=your_database_url
```

## 🔧 Production Configuration

### 1. Environment Variables

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://user:pass@db:5432/hummingbird_monitor
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your_very_secure_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
CORS_ORIGINS=https://yourdomain.com

# AI Services
OPENAI_API_KEY=your_production_openai_key
CODEPROJECT_AI_URL=http://ai-server:32168

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
PROMETHEUS_ENABLED=true
```

### 2. Database Configuration

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 3. Logging Configuration

```python
# backend/logging_config.py
import logging
import logging.handlers
from datetime import datetime

def setup_production_logging():
    # Configure structured logging
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/hummingbird_monitor.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.handlers.SysLogHandler()
        ]
    )
```

### 4. Security Configuration

```python
# backend/app/core/security.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 📊 Monitoring and Observability

### 1. Prometheus Metrics

```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

### 2. Health Checks

```python
# backend/app/api/routes/health.py
from fastapi import APIRouter
from app.core.database import engine
import psutil

router = APIRouter()

@router.get("/health")
async def health_check():
    # Check database
    try:
        engine.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "cpu_usage": cpu_percent,
        "memory_usage": memory_percent,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 3. Log Aggregation

```yaml
# docker-compose.yml
services:
  # ... existing services ...
  
  # ELK Stack for log aggregation
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## 🔄 CI/CD Pipeline

### 1. GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python -m pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Deploy to your production environment
          ssh user@your-server "cd /path/to/app && docker-compose pull && docker-compose up -d"
```

### 2. Automated Testing

```python
# tests/test_deployment.py
import pytest
import requests
from app.core.database import engine

def test_database_connection():
    """Test database connection"""
    result = engine.execute("SELECT 1").fetchone()
    assert result[0] == 1

def test_api_health():
    """Test API health endpoint"""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_frontend_accessibility():
    """Test frontend accessibility"""
    response = requests.get("http://localhost:3000")
    assert response.status_code == 200
```

## 🚀 Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_visits_bird_id ON visits(bird_id);
CREATE INDEX CONCURRENTLY idx_visits_feeder_id ON visits(feeder_id);
CREATE INDEX CONCURRENTLY idx_visits_visit_time ON visits(visit_time);
CREATE INDEX CONCURRENTLY idx_visits_created_at ON visits(created_at);

-- Analyze tables for better query planning
ANALYZE visits;
ANALYZE birds;
ANALYZE alerts;
```

### 2. Caching Strategy

```python
# backend/app/core/cache.py
import redis
from functools import wraps

redis_client = redis.Redis.from_url(REDIS_URL)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

### 3. Load Balancing

```nginx
# nginx.conf
upstream backend {
    least_conn;
    server backend1:8000 weight=3;
    server backend2:8000 weight=3;
    server backend3:8000 weight=2;
}

upstream frontend {
    server frontend1:3000;
    server frontend2:3000;
}

server {
    listen 80;
    
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔒 Security Best Practices

### 1. SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
}
```

### 2. Authentication and Authorization

```python
# backend/app/core/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 3. Input Validation

```python
# backend/app/schemas/validation.py
from pydantic import BaseModel, validator
import re

class BirdCreate(BaseModel):
    name: str
    species: str
    description: str = None
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Name contains invalid characters')
        return v
    
    @validator('species')
    def validate_species(cls, v):
        if not re.match(r'^[a-zA-Z\s\-]+$', v):
            raise ValueError('Species contains invalid characters')
        return v
```

## 📈 Scaling Strategies

### 1. Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hummingbird_monitor
      - REDIS_URL=redis://redis:6379
```

### 2. Database Scaling

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Read replica configuration
READ_DATABASE_URL = "postgresql://user:pass@read-replica:5432/hummingbird_monitor"
WRITE_DATABASE_URL = "postgresql://user:pass@master:5432/hummingbird_monitor"

read_engine = create_engine(READ_DATABASE_URL)
write_engine = create_engine(WRITE_DATABASE_URL)
```

### 3. Microservices Architecture

```yaml
# docker-compose.yml
services:
  # Bird identification service
  bird-identification:
    build: ./services/bird-identification
    environment:
      - CODEPROJECT_AI_URL=http://ai-server:32168
    ports:
      - "8001:8000"
  
  # Visit tracking service
  visit-tracking:
    build: ./services/visit-tracking
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hummingbird_monitor
    ports:
      - "8002:8000"
  
  # Alert service
  alert-service:
    build: ./services/alert-service
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hummingbird_monitor
      - REDIS_URL=redis://redis:6379
    ports:
      - "8003:8000"
```

This comprehensive deployment guide covers various deployment scenarios and best practices for the Hummingbird Monitor system. Choose the approach that best fits your infrastructure and requirements.
