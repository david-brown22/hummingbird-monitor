"""
Database initialization script
"""

import asyncio
from app.core.database import engine, Base
from app.models import bird, visit, alert, summary

async def init_database():
    """Initialize the database with all tables"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("Tables created:")
    print("- birds")
    print("- visits") 
    print("- alerts")
    print("- summaries")

if __name__ == "__main__":
    asyncio.run(init_database())
