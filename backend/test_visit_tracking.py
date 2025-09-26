"""
Test script for visit tracking system
"""

import asyncio
from datetime import datetime, date, timedelta
from app.services.visit_tracker import VisitTrackerService
from app.core.database import SessionLocal, engine
from app.models import bird, visit, alert, summary

async def test_visit_tracking():
    """Test the visit tracking service"""
    print("🧪 Testing Visit Tracking Service")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        visit_tracker = VisitTrackerService()
        
        # Test recording visits
        print("📝 Testing visit recording...")
        
        test_visits = [
            {
                "bird_id": 1,
                "feeder_id": "feeder_001",
                "camera_id": "camera_001",
                "duration_seconds": 15.5,
                "confidence_score": 0.95,
                "temperature": 72.5,
                "weather_condition": "sunny"
            },
            {
                "bird_id": 2,
                "feeder_id": "feeder_001",
                "camera_id": "camera_001",
                "duration_seconds": 22.3,
                "confidence_score": 0.87,
                "temperature": 73.0,
                "weather_condition": "sunny"
            },
            {
                "bird_id": None,  # Unidentified bird
                "feeder_id": "feeder_002",
                "camera_id": "camera_002",
                "duration_seconds": 8.7,
                "confidence_score": 0.45,
                "temperature": 71.8,
                "weather_condition": "cloudy"
            },
            {
                "bird_id": 1,  # Same bird as first visit
                "feeder_id": "feeder_001",
                "camera_id": "camera_001",
                "duration_seconds": 18.2,
                "confidence_score": 0.92,
                "temperature": 74.1,
                "weather_condition": "sunny"
            }
        ]
        
        recorded_visits = []
        for i, visit_data in enumerate(test_visits):
            result = await visit_tracker.record_visit(
                bird_id=visit_data["bird_id"],
                feeder_id=visit_data["feeder_id"],
                camera_id=visit_data["camera_id"],
                duration_seconds=visit_data["duration_seconds"],
                confidence_score=visit_data["confidence_score"],
                temperature=visit_data["temperature"],
                weather_condition=visit_data["weather_condition"],
                db=db
            )
            
            print(f"✅ Visit {i+1}: {result['success']}")
            if result["success"]:
                recorded_visits.append(result)
                print(f"   - Visit ID: {result['visit_id']}")
                print(f"   - Bird ID: {result['bird_id']}")
                print(f"   - Alert Triggered: {result['alert_triggered']}")
            else:
                print(f"   - Error: {result.get('error')}")
        
        # Test visit counts
        print("\n📊 Testing visit counts...")
        
        counts = await visit_tracker.get_visit_counts(
            start_date=date.today(),
            end_date=date.today(),
            db=db
        )
        
        print(f"✅ Today's visit counts:")
        print(f"   - Total visits: {counts['total_visits']}")
        print(f"   - Identified visits: {counts['identified_visits']}")
        print(f"   - Unidentified visits: {counts['unidentified_visits']}")
        print(f"   - Unique birds: {counts['unique_birds']}")
        print(f"   - Average duration: {counts['average_duration']:.2f}s")
        print(f"   - Peak hour: {counts['peak_hour']}")
        
        # Test daily summary
        print("\n📅 Testing daily summary...")
        
        daily_summary = await visit_tracker.get_daily_visit_summary(
            target_date=date.today(),
            db=db
        )
        
        print(f"✅ Daily summary:")
        print(f"   - Date: {daily_summary['date']}")
        print(f"   - Total visits: {daily_summary['total_visits']}")
        print(f"   - Unique birds: {daily_summary['unique_birds']}")
        print(f"   - Peak hour: {daily_summary['peak_hour']}")
        print(f"   - Weather: {daily_summary['weather_summary']}")
        print(f"   - Temperature: {daily_summary['temperature_range']}")
        
        # Test bird history
        print("\n🐦 Testing bird visit history...")
        
        bird_history = await visit_tracker.get_bird_visit_history(
            bird_id=1,
            days=7,
            db=db
        )
        
        print(f"✅ Bird 1 history:")
        print(f"   - Total visits: {bird_history['total_visits']}")
        print(f"   - Average duration: {bird_history['average_duration']:.2f}s")
        print(f"   - Peak hour: {bird_history['peak_hour']}")
        print(f"   - Recent visits: {len(bird_history['recent_visits'])}")
        
        # Test feeder statistics
        print("\n🍯 Testing feeder statistics...")
        
        feeder_stats = await visit_tracker.get_feeder_statistics(
            feeder_id="feeder_001",
            days=7,
            db=db
        )
        
        print(f"✅ Feeder 001 statistics:")
        print(f"   - Total visits: {feeder_stats['total_visits']}")
        print(f"   - Unique birds: {feeder_stats['unique_birds']}")
        print(f"   - Average daily visits: {feeder_stats['average_daily_visits']}")
        print(f"   - Peak hour: {feeder_stats['peak_hour']}")
        print(f"   - Nectar estimate: {feeder_stats['nectar_estimate']['remaining_percentage']:.1f}%")
        print(f"   - Needs refill: {feeder_stats['nectar_estimate']['needs_refill']}")
        
        print("\n✅ Visit tracking test completed successfully!")
        
    except Exception as e:
        print(f"❌ Visit tracking test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_visit_tracking_api():
    """Test the visit tracking API endpoints"""
    print("\n🌐 Testing Visit Tracking API")
    print("=" * 50)
    
    # This would test the actual API endpoints
    # For now, we'll just print the available endpoints
    
    endpoints = [
        "POST /api/visit-tracking/record - Record a new visit",
        "GET /api/visit-tracking/counts - Get visit counts with filters",
        "GET /api/visit-tracking/daily-summary - Get daily visit summary",
        "GET /api/visit-tracking/bird/{bird_id}/history - Get bird visit history",
        "GET /api/visit-tracking/feeder/{feeder_id}/stats - Get feeder statistics",
        "GET /api/visit-tracking/trends - Get visit trends over time",
        "GET /api/visit-tracking/analytics - Get comprehensive analytics",
        "GET /api/visit-tracking/health - Health check"
    ]
    
    print("Available API endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    print("\n✅ API endpoints documented!")

async def test_visit_analytics():
    """Test visit analytics and reporting"""
    print("\n📈 Testing Visit Analytics")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        from app.models.visit import Visit
        from sqlalchemy import func
        
        # Test analytics queries
        print("Testing analytics queries...")
        
        # Get overall statistics
        total_visits = db.query(Visit).count()
        identified_visits = db.query(Visit).filter(Visit.bird_id.isnot(None)).count()
        
        print(f"✅ Overall statistics:")
        print(f"   - Total visits: {total_visits}")
        print(f"   - Identified visits: {identified_visits}")
        print(f"   - Identification rate: {identified_visits/total_visits*100:.1f}%" if total_visits > 0 else "   - Identification rate: 0%")
        
        # Get feeder breakdown
        feeder_breakdown = db.query(
            Visit.feeder_id,
            func.count(Visit.id).label('count')
        ).group_by(Visit.feeder_id).all()
        
        print(f"✅ Feeder breakdown:")
        for feeder in feeder_breakdown:
            print(f"   - {feeder.feeder_id}: {feeder.count} visits")
        
        # Get hourly distribution
        hourly_dist = db.query(
            func.extract('hour', Visit.visit_time).label('hour'),
            func.count(Visit.id).label('count')
        ).group_by(func.extract('hour', Visit.visit_time)).all()
        
        print(f"✅ Hourly distribution:")
        for hour in sorted(hourly_dist, key=lambda x: x.hour):
            print(f"   - {int(hour.hour):02d}:00: {hour.count} visits")
        
        print("\n✅ Analytics test completed!")
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def main():
    """Run all visit tracking tests"""
    print("🐦 Hummingbird Monitor - Visit Tracking Test Suite")
    print("=" * 70)
    
    # Run tests
    await test_visit_tracking()
    await test_visit_tracking_api()
    await test_visit_analytics()
    
    print("\n🎉 All visit tracking tests completed!")
    print("\n📚 Next steps:")
    print("1. Start the API server: python run_server.py")
    print("2. Test API endpoints: http://localhost:8000/docs")
    print("3. Record test visits: POST /api/visit-tracking/record")
    print("4. View analytics: GET /api/visit-tracking/analytics")

if __name__ == "__main__":
    asyncio.run(main())
