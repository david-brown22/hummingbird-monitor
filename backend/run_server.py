"""
Run the FastAPI server for development
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting Hummingbird Monitor API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
