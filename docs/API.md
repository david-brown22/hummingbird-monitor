# 📚 Hummingbird Monitor API Documentation

## Overview

The Hummingbird Monitor API provides comprehensive endpoints for managing bird visits, identification, alerts, and system monitoring. Built with FastAPI, it offers automatic documentation, request validation, and high performance.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com/api`

## Authentication

Currently, the API uses simple authentication. For production, implement proper JWT or OAuth2 authentication.

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes:

```json
{
  "success": false,
  "error": "Error message",
  "details": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🐦 Core Services

### Birds API

#### Get All Birds
```http
GET /api/birds
```

**Response:**
```json
{
  "birds": [
    {
      "id": 1,
      "name": "Ruby",
      "species": "Ruby-throated Hummingbird",
      "first_seen": "2024-01-01T00:00:00Z",
      "last_seen": "2024-01-15T10:30:00Z",
      "total_visits": 45,
      "embedding_id": "bird_1_embedding"
    }
  ]
}
```

#### Get Bird by ID
```http
GET /api/birds/{bird_id}
```

#### Create New Bird
```http
POST /api/birds
Content-Type: application/json

{
  "name": "Ruby",
  "species": "Ruby-throated Hummingbird",
  "description": "Frequent visitor to feeder 1"
}
```

#### Update Bird
```http
PUT /api/birds/{bird_id}
Content-Type: application/json

{
  "name": "Ruby Updated",
  "species": "Ruby-throated Hummingbird"
}
```

#### Delete Bird
```http
DELETE /api/birds/{bird_id}
```

### Visits API

#### Get All Visits
```http
GET /api/visits?limit=50&offset=0&bird_id=1&feeder_id=feeder_001
```

**Query Parameters:**
- `limit`: Number of visits to return (default: 50)
- `offset`: Number of visits to skip (default: 0)
- `bird_id`: Filter by bird ID
- `feeder_id`: Filter by feeder ID
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)

#### Create New Visit
```http
POST /api/visits
Content-Type: application/json

{
  "bird_id": 1,
  "feeder_id": "feeder_001",
  "camera_id": "camera_001",
  "duration_seconds": 15.5,
  "confidence_score": 0.95,
  "temperature": 72.5,
  "weather_condition": "sunny"
}
```

#### Get Visit by ID
```http
GET /api/visits/{visit_id}
```

#### Update Visit
```http
PUT /api/visits/{visit_id}
Content-Type: application/json

{
  "duration_seconds": 20.0,
  "confidence_score": 0.98
}
```

#### Delete Visit
```http
DELETE /api/visits/{visit_id}
```

### Alerts API

#### Get All Alerts
```http
GET /api/alerts?status=active&severity=high
```

**Query Parameters:**
- `status`: Filter by status (active, resolved)
- `severity`: Filter by severity (low, medium, high)
- `feeder_id`: Filter by feeder ID

#### Create New Alert
```http
POST /api/alerts
Content-Type: application/json

{
  "feeder_id": "feeder_001",
  "alert_type": "refill_needed",
  "title": "Feeder 001 Needs Refilling",
  "message": "Feeder 001 is running low on nectar",
  "severity": "medium"
}
```

#### Update Alert
```http
PUT /api/alerts/{alert_id}
Content-Type: application/json

{
  "status": "resolved",
  "resolution_notes": "Feeder refilled at 2:30 PM"
}
```

#### Delete Alert
```http
DELETE /api/alerts/{alert_id}
```

### Summaries API

#### Get All Summaries
```http
GET /api/summaries?date=2024-01-15&feeder_id=feeder_001
```

#### Create New Summary
```http
POST /api/summaries
Content-Type: application/json

{
  "date": "2024-01-15",
  "feeder_id": "feeder_001",
  "summary_text": "Busy day with 25 visits from 8 different birds",
  "visit_count": 25,
  "unique_birds": 8
}
```

## 🤖 AI Services

### Bird Identification API

#### Identify Bird from Image
```http
POST /api/identification/identify
Content-Type: multipart/form-data

file: [image_file]
feeder_id: feeder_001
camera_id: camera_001
```

**Response:**
```json
{
  "bird_id": 1,
  "bird_name": "Ruby",
  "confidence": 0.95,
  "species": "Ruby-throated Hummingbird",
  "visit_recorded": true,
  "visit_id": 123
}
```

#### Add Bird to Database
```http
POST /api/identification/add-bird/{bird_id}
Content-Type: application/json

{
  "name": "New Bird",
  "species": "Anna's Hummingbird",
  "description": "New visitor to the garden"
}
```

#### Update Bird Embedding
```http
PUT /api/identification/update-bird/{bird_id}
Content-Type: multipart/form-data

file: [image_file]
```

#### Remove Bird from Database
```http
DELETE /api/identification/remove-bird/{bird_id}
```

#### Get Bird Embedding
```http
GET /api/identification/bird/{bird_id}/embedding
```

#### Search Similar Birds
```http
POST /api/identification/search-similar
Content-Type: multipart/form-data

file: [image_file]
limit: 5
```

#### Get Database Statistics
```http
GET /api/identification/stats
```

#### Rebuild Database
```http
POST /api/identification/rebuild-database
```

### Summary Generation API

#### Generate Daily Summary
```http
POST /api/summary-generation/daily?target_date=2024-01-15
```

**Response:**
```json
{
  "date": "2024-01-15",
  "title": "Daily Hummingbird Activity - January 15, 2024",
  "content": "Today was a busy day with 25 visits from 8 different birds...",
  "total_visits": 25,
  "unique_birds": 8,
  "peak_hour": "14:00",
  "average_duration": 18.5,
  "weather_summary": "Sunny, 72°F",
  "model_used": "gpt-3.5-turbo",
  "confidence_score": 0.85
}
```

#### Generate Weekly Summary
```http
POST /api/summary-generation/weekly?target_date=2024-01-15
```

#### Generate Bird Profile
```http
POST /api/summary-generation/bird/{bird_id}/profile?days=30
```

#### Generate Feeder Analysis
```http
POST /api/summary-generation/feeder/{feeder_id}/analysis?days=7
```

#### Generate Alert Summary
```http
POST /api/summary-generation/alert/{alert_id}/summary
```

## 📊 Visit Tracking API

#### Record Visit
```http
POST /api/visit-tracking/record
Content-Type: application/json

{
  "bird_id": 1,
  "feeder_id": "feeder_001",
  "camera_id": "camera_001",
  "duration_seconds": 15.5,
  "confidence_score": 0.95,
  "temperature": 72.5,
  "weather_condition": "sunny"
}
```

#### Get Visit Counts
```http
GET /api/visit-tracking/counts?start_date=2024-01-15&end_date=2024-01-15&feeder_id=feeder_001
```

#### Get Daily Summary
```http
GET /api/visit-tracking/daily-summary?target_date=2024-01-15
```

#### Get Bird History
```http
GET /api/visit-tracking/bird/{bird_id}/history?days=30
```

#### Get Feeder Statistics
```http
GET /api/visit-tracking/feeder/{feeder_id}/stats?days=7
```

#### Get Visit Trends
```http
GET /api/visit-tracking/trends?days=7&feeder_id=feeder_001
```

#### Get Visit Analytics
```http
GET /api/visit-tracking/analytics?days=30
```

## 🍯 Feeder Alerts API

#### Calculate Nectar Depletion
```http
GET /api/feeder-alerts/feeder/{feeder_id}/depletion?days=7
```

**Response:**
```json
{
  "feeder_id": "feeder_001",
  "total_visits": 45,
  "estimated_depletion": 22.5,
  "remaining_nectar": 77.5,
  "depletion_percentage": 22.5,
  "alert_level": "info",
  "days_until_empty": 3.2,
  "recommendations": [
    "Refill within 2-3 days",
    "Monitor depletion rate"
  ]
}
```

#### Check Alert Conditions
```http
POST /api/feeder-alerts/feeder/{feeder_id}/check-alerts
```

#### Get Alert History
```http
GET /api/feeder-alerts/feeder/{feeder_id}/history?days=30
```

#### Predict Feeder Needs
```http
GET /api/feeder-alerts/feeder/{feeder_id}/predict?days_ahead=7
```

#### Get System Alert Overview
```http
GET /api/feeder-alerts/system/overview
```

#### Mark Feeder as Refilled
```http
POST /api/feeder-alerts/feeder/{feeder_id}/refill?refill_amount=100.0
```

#### Get Active Alerts
```http
GET /api/feeder-alerts/alerts/active?severity=high&feeder_id=feeder_001
```

## 📈 Observability API

#### Get System Metrics
```http
GET /api/observability/metrics
```

**Response:**
```json
{
  "metrics": {
    "system": {
      "uptime_seconds": 3600,
      "total_requests": 150,
      "successful_requests": 145,
      "failed_requests": 5,
      "average_response_time": 0.5,
      "health_score": 85.5
    },
    "visits": {
      "total_visits": 250,
      "identified_visits": 200,
      "unique_birds": 12,
      "average_duration": 18.5,
      "peak_hour": 14
    }
  },
  "performance": { ... },
  "logs": [ ... ],
  "health_score": 85.5
}
```

#### Get Health Status
```http
GET /api/observability/health
```

#### Get Performance Analysis
```http
GET /api/observability/performance
```

#### Get Logs
```http
GET /api/observability/logs?level=ERROR&service=bird_identification&limit=50
```

**Query Parameters:**
- `level`: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service`: Filter by service name
- `limit`: Maximum number of logs to return
- `start_time`: Filter by start time (ISO format)
- `end_time`: Filter by end time (ISO format)

#### Log Event
```http
POST /api/observability/log
Content-Type: application/json

{
  "event_type": "visit_recorded",
  "message": "New visit recorded",
  "level": "INFO",
  "service": "visit_tracker",
  "metadata": {
    "feeder_id": "feeder_001",
    "bird_id": 1
  }
}
```

#### Record Metric
```http
POST /api/observability/metric
Content-Type: application/json

{
  "metric_name": "visit_count",
  "value": 1.0,
  "metric_type": "counter",
  "tags": {
    "feeder_id": "feeder_001"
  }
}
```

#### Record Performance Data
```http
POST /api/observability/performance
Content-Type: application/json

{
  "operation": "bird_identification",
  "duration": 1.5,
  "success": true,
  "metadata": {
    "bird_id": 1,
    "confidence": 0.95
  }
}
```

#### Get Observability Dashboard
```http
GET /api/observability/dashboard
```

#### Get Alert Status
```http
GET /api/observability/alerts/status
```

#### Get System Information
```http
GET /api/observability/system/info
```

#### Get Configuration
```http
GET /api/observability/config
```

#### Health Check
```http
GET /api/observability/health/check
```

## 📷 Capture Ingestion API

#### Process Capture
```http
POST /api/captures/process
Content-Type: multipart/form-data

file: [image_file]
feeder_id: feeder_001
camera_id: camera_001
motion_data: {
  "motion_detected": true,
  "confidence": 0.85,
  "region": "center"
}
```

#### Blue Iris Webhook
```http
POST /api/captures/webhook/blue-iris
Content-Type: application/json

{
  "camera": "Camera 1",
  "trigger": "motion",
  "timestamp": "2024-01-15T10:30:00Z",
  "image_url": "http://blueiris/image.jpg"
}
```

#### Get Capture Statistics
```http
GET /api/captures/stats
```

#### Health Check
```http
GET /api/captures/health
```

## 🔧 Blue Iris Integration API

#### Authenticate with Blue Iris
```http
POST /api/blue-iris/auth
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

#### Get Camera List
```http
GET /api/blue-iris/cameras
```

#### Get Camera Status
```http
GET /api/blue-iris/camera/{camera_id}/status
```

#### Configure Webhook
```http
POST /api/blue-iris/webhook/configure
Content-Type: application/json

{
  "webhook_url": "http://your-server:8000/api/captures/webhook/blue-iris",
  "events": ["motion", "alert"]
}
```

#### Test Webhook
```http
POST /api/blue-iris/webhook/test
```

#### Get Motion Alerts
```http
GET /api/blue-iris/alerts/motion?camera_id=camera_001&start_time=2024-01-15T00:00:00Z
```

## 📊 Data Models

### Bird Model
```json
{
  "id": 1,
  "name": "Ruby",
  "species": "Ruby-throated Hummingbird",
  "description": "Frequent visitor to feeder 1",
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2024-01-15T10:30:00Z",
  "total_visits": 45,
  "embedding_id": "bird_1_embedding",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Visit Model
```json
{
  "id": 123,
  "bird_id": 1,
  "feeder_id": "feeder_001",
  "camera_id": "camera_001",
  "visit_time": "2024-01-15T10:30:00Z",
  "duration_seconds": 15.5,
  "confidence_score": 0.95,
  "image_path": "/images/visit_123.jpg",
  "video_path": "/videos/visit_123.mp4",
  "motion_triggered": true,
  "temperature": 72.5,
  "weather_condition": "sunny",
  "detection_metadata": {
    "bounding_box": [100, 100, 200, 200],
    "confidence": 0.95
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Alert Model
```json
{
  "id": 1,
  "feeder_id": "feeder_001",
  "alert_type": "refill_needed",
  "title": "Feeder 001 Needs Refilling",
  "message": "Feeder 001 is running low on nectar",
  "severity": "medium",
  "status": "active",
  "visit_count": 45,
  "estimated_nectar_level": 25.5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "resolved_at": null
}
```

### Summary Model
```json
{
  "id": 1,
  "date": "2024-01-15",
  "feeder_id": "feeder_001",
  "summary_text": "Busy day with 25 visits from 8 different birds",
  "visit_count": 25,
  "unique_birds": 8,
  "peak_hours": "14:00-16:00",
  "new_birds_identified": 2,
  "created_at": "2024-01-15T23:59:59Z",
  "updated_at": "2024-01-15T23:59:59Z"
}
```

## 🔒 Security Considerations

### Authentication
- Implement JWT tokens for production
- Use HTTPS for all communications
- Validate all input data
- Implement rate limiting

### Data Protection
- Encrypt sensitive data
- Use secure database connections
- Implement proper access controls
- Regular security audits

### API Security
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

## 📈 Performance Considerations

### Caching
- Implement response caching
- Use Redis for session storage
- Cache frequently accessed data
- Optimize database queries

### Rate Limiting
- Implement API rate limiting
- Use connection pooling
- Optimize response times
- Monitor performance metrics

### Scalability
- Use load balancers
- Implement horizontal scaling
- Optimize database performance
- Use CDN for static assets

## 🧪 Testing

### API Testing
```bash
# Test all endpoints
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/api/observability/health
curl -X GET http://localhost:8000/api/birds
```

### Load Testing
```bash
# Use tools like Apache Bench or wrk
ab -n 1000 -c 10 http://localhost:8000/api/birds
```

### Integration Testing
```bash
# Run integration tests
python -m pytest tests/integration/
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [API Security Guidelines](https://owasp.org/www-project-api-security/)

This comprehensive API documentation provides all the information needed to integrate with the Hummingbird Monitor system. For additional help, refer to the interactive API documentation at `/docs` when running the server.
