# Hummingbird Monitor

An AI-powered application for tracking hummingbird visits, generating daily summaries, and alerting feeder status. Built with Python FastAPI backend and React frontend.

## 🐦 Features

- **Motion Detection**: Receives motion-triggered frames from Blue Iris
- **AI Bird Identification**: Uses CodeProject.AI and embeddings to identify individual birds
- **Visit Tracking**: Counts visits per bird, per feeder, per day
- **Daily Summaries**: AI-generated daily activity summaries using LangChain
- **Smart Alerts**: Alerts when feeders need refilling based on visit frequency
- **Modern Dashboard**: Clean, responsive React interface
- **Observability**: Comprehensive logging and metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Blue Iris    │    │   CodeProject   │    │   Pinecone/     │
│   Camera       │───▶│   AI Detection  │───▶│   FAISS        │
│   System       │    │   Service       │    │   Embeddings   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │   Capture  │ │   Bird      │ │   Visit     │ │ Summary  │ │
│  │  Ingestion │ │Identification│ │  Counter    │ │Generator │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │   Alert     │ │   Database  │ │   API      │ │Observability│ │
│  │   Logic     │ │   (SQLite)  │ │  Routes    │ │          │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │ Dashboard  │ │   Birds    │ │   Visits   │ │ Alerts   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │ Summaries  │ │  Settings  │ │   Charts   │ │  Layout  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- CodeProject.AI (for object detection)
- Blue Iris (optional, for camera integration)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/david-brown22/hummingbird-monitor.git
   cd hummingbird-monitor
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and settings
   ```

4. **Initialize database**
   ```bash
   python main.py
   ```

5. **Start the backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Open in browser**
   ```
   http://localhost:3000
   ```

## 📋 API Endpoints

### Birds
- `GET /api/birds/` - List all birds
- `POST /api/birds/` - Create new bird
- `GET /api/birds/{id}` - Get bird details
- `PUT /api/birds/{id}` - Update bird
- `DELETE /api/birds/{id}` - Delete bird

### Visits
- `GET /api/visits/` - List visits with filtering
- `POST /api/visits/` - Create visit record
- `POST /api/visits/process-image` - Process motion image
- `GET /api/visits/stats/daily` - Daily visit statistics

### Alerts
- `GET /api/alerts/` - List alerts
- `POST /api/alerts/` - Create alert
- `PUT /api/alerts/{id}/acknowledge` - Acknowledge alert
- `PUT /api/alerts/{id}/dismiss` - Dismiss alert

### Summaries
- `GET /api/summaries/` - List summaries
- `POST /api/summaries/generate/{date}` - Generate daily summary
- `GET /api/summaries/latest` - Get latest summary

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./hummingbird_monitor.db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone (for vector embeddings)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=hummingbird-embeddings

# CodeProject.AI
CODEPROJECT_AI_URL=http://localhost:32168

# Blue Iris (optional)
BLUE_IRIS_URL=http://your-blue-iris-server:port
BLUE_IRIS_USERNAME=your_username
BLUE_IRIS_PASSWORD=your_password

# Alert Settings
VISIT_THRESHOLD_FOR_ALERT=50
NECTAR_DEPLETION_RATE=0.1
```

## 🧠 AI Integration

### Bird Identification Pipeline

1. **Motion Detection**: Blue Iris triggers on motion
2. **Object Detection**: CodeProject.AI identifies birds in frame
3. **Feature Extraction**: Generate embeddings from bird region
4. **Vector Matching**: Compare against known birds in Pinecone/FAISS
5. **Confidence Scoring**: Assign confidence to identification

### Daily Summary Generation

1. **Data Aggregation**: Collect daily visit statistics
2. **LangChain Processing**: Use OpenAI to generate summaries
3. **Pattern Analysis**: Identify trends and unusual activity
4. **Natural Language**: Generate human-readable summaries

## 📊 Dashboard Features

- **Real-time Statistics**: Live visit counts and bird activity
- **Interactive Charts**: 7-day trends and hourly patterns
- **Bird Profiles**: Individual bird tracking and history
- **Alert Management**: Feeder status and refill notifications
- **Summary Viewing**: AI-generated daily reports
- **Settings Panel**: Configurable thresholds and preferences

## 🔍 Monitoring & Observability

- **Visit Tracking**: Complete audit trail of all visits
- **Performance Metrics**: System performance and AI accuracy
- **Error Logging**: Comprehensive error tracking
- **Alert History**: Complete alert lifecycle tracking

## 🛠️ Development

### Project Structure

```
hummingbird-monitor/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── App.js         # Main app component
│   └── package.json       # Node dependencies
└── README.md
```

### Adding New Features

1. **Backend**: Add models, schemas, routes, and services
2. **Frontend**: Create components and pages
3. **Integration**: Connect frontend to backend APIs
4. **Testing**: Add unit and integration tests

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the architecture diagram in `architecture.md`

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [React](https://reactjs.org/)
- AI capabilities via [LangChain](https://langchain.com/)
- Object detection with [CodeProject.AI](https://www.codeproject.com/Articles/5322557/CodeProject-AI-Server)
- Vector storage with [Pinecone](https://www.pinecone.io/)