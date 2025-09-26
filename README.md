# hummingbird-monitor
AI-powered app for tracking hummingbird visits, generating daily summaries, and alerting feeder status.

# Hummingbird Monitoring and Alert System

This project uses AI to monitor hummingbird activity via motion-triggered video feeds, identify individual birds, count visits, generate daily summaries, and alert when feeders need refilling. It combines Python for backend logic and React for the frontend dashboard.

## Features
- Motion-triggered frame ingestion from Blue Iris
- AI-based bird identification using embeddings
- Visit tracking per bird and per feeder
- Daily summary generation via prompt chaining
- Feeder refill alerts based on visit frequency
- React dashboard for observability and control

## Tech Stack
- Python (FastAPI or Flask)
- LangChain for prompt chaining and RAG logic
- CodeProject.AI for object detection
- Pinecone or FAISS for bird ID embeddings
- React + Node.js for frontend
- Cursor IDE for development
- GitHub for version control

## Setup
1. Clone the repo
2. Install Python dependencies (`pip install -r requirements.txt`)
3. Install Node dependencies (`npm install` in `/frontend`)
4. Run backend and frontend servers
5. Connect Blue Iris and CodeProject.AI
6. View dashboard and monitor activity

## License
MIT