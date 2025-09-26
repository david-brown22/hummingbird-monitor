"""
Hummingbird Monitoring and Alert System - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.api.routes import birds, visits, alerts, summaries, captures, identification, visit_tracking, summary_generation, feeder_alerts
from app.core.database import init_db

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="Hummingbird Monitor API",
    description="AI-powered hummingbird monitoring and alert system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(birds.router, prefix="/api/birds", tags=["birds"])
app.include_router(visits.router, prefix="/api/visits", tags=["visits"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(summaries.router, prefix="/api/summaries", tags=["summaries"])
app.include_router(captures.router, prefix="/api/captures", tags=["captures"])
app.include_router(identification.router, prefix="/api/identification", tags=["identification"])
app.include_router(visit_tracking.router, prefix="/api/visit-tracking", tags=["visit-tracking"])
app.include_router(summary_generation.router, prefix="/api/summary-generation", tags=["summary-generation"])
app.include_router(feeder_alerts.router, prefix="/api/feeder-alerts", tags=["feeder-alerts"])

# Serve static files (for React build)
if os.path.exists("frontend/build"):
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hummingbird Monitor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
