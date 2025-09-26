"""
Test database connection and basic operations
"""

import asyncio
from sqlalchemy.orm import sessionmaker
from app.core.database import engine, get_db
from app.models.bird import Bird
from app.models.visit import Visit
from app.models.alert import Alert
from app.models.summary import Summary
from datetime import datetime

async def test_database():
    """Test database operations"""
    print("Testing database connection...")
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test creating a bird
        print("Creating test bird...")
        test_bird = Bird(
            name="Test Hummingbird",
            embedding_id="test_embedding_123",
            dominant_colors='["red", "green"]',
            size_estimate=8.5,
            distinctive_features="Small hummingbird with red throat"
        )
        db.add(test_bird)
        db.commit()
        db.refresh(test_bird)
        print(f"Created bird with ID: {test_bird.id}")
        
        # Test creating a visit
        print("Creating test visit...")
        test_visit = Visit(
            bird_id=test_bird.id,
            feeder_id="feeder_001",
            camera_id="camera_001",
            visit_time=datetime.now(),
            duration_seconds=15.5,
            confidence_score=0.95,
            motion_triggered="true"
        )
        db.add(test_visit)
        db.commit()
        db.refresh(test_visit)
        print(f"Created visit with ID: {test_visit.id}")
        
        # Test creating an alert
        print("Creating test alert...")
        test_alert = Alert(
            feeder_id="feeder_001",
            alert_type="refill_needed",
            title="Feeder Refill Required",
            message="Feeder 001 needs refilling based on visit frequency",
            severity="medium",
            visit_count=45
        )
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        print(f"Created alert with ID: {test_alert.id}")
        
        # Test creating a summary
        print("Creating test summary...")
        test_summary = Summary(
            date=datetime.now().date(),
            title="Daily Activity Summary",
            content="Today we observed 12 visits from 3 different hummingbirds...",
            total_visits=12,
            unique_birds=3,
            peak_hour="10:00"
        )
        db.add(test_summary)
        db.commit()
        db.refresh(test_summary)
        print(f"Created summary with ID: {test_summary.id}")
        
        # Test queries
        print("\nTesting queries...")
        birds = db.query(Bird).all()
        visits = db.query(Visit).all()
        alerts = db.query(Alert).all()
        summaries = db.query(Summary).all()
        
        print(f"Found {len(birds)} birds")
        print(f"Found {len(visits)} visits")
        print(f"Found {len(alerts)} alerts")
        print(f"Found {len(summaries)} summaries")
        
        print("\nDatabase test completed successfully! ✅")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_database())
