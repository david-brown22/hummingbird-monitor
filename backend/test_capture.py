"""
Test script for capture ingestion functionality
"""

import asyncio
import os
from pathlib import Path
from app.services.capture_ingestion import CaptureIngestionService
from app.core.database import SessionLocal, engine
from app.models import bird, visit, alert, summary

async def test_capture_ingestion():
    """Test the capture ingestion service"""
    print("🧪 Testing Capture Ingestion Service")
    print("=" * 50)
    
    # Create test image directory
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_path = test_dir / "test_hummingbird.png"
    
    # Create a minimal PNG file for testing
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\xd7\xd4\xf8\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open(test_image_path, "wb") as f:
        f.write(png_data)
    
    print(f"✅ Created test image: {test_image_path}")
    
    # Test capture ingestion service
    capture_service = CaptureIngestionService()
    
    # Test motion data
    motion_data = {
        "trigger_type": "motion",
        "timestamp": "2024-01-15T10:30:00Z",
        "camera_name": "front_camera",
        "duration_seconds": 15.5,
        "temperature": 72.5,
        "weather_condition": "sunny"
    }
    
    print("\n📸 Testing motion capture processing...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test processing motion capture
        result = await capture_service.process_motion_capture(
            image_path=str(test_image_path),
            feeder_id="feeder_001",
            camera_id="camera_001",
            motion_data=motion_data,
            db=db
        )
        
        print(f"✅ Capture processing result:")
        print(f"   Success: {result['success']}")
        print(f"   Visit ID: {result.get('visit_id')}")
        print(f"   Bird ID: {result.get('bird_id')}")
        print(f"   Confidence: {result.get('confidence', 0.0)}")
        print(f"   Alert Triggered: {result.get('alert_triggered', False)}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
        
        # Test webhook processing
        print("\n🔗 Testing Blue Iris webhook processing...")
        
        webhook_data = {
            "camera": "front_camera",
            "trigger": "motion",
            "timestamp": "2024-01-15T10:30:00Z",
            "image_path": str(test_image_path)
        }
        
        webhook_result = await capture_service.process_blue_iris_webhook(webhook_data)
        
        print(f"✅ Webhook processing result:")
        print(f"   Success: {webhook_result['success']}")
        print(f"   Visit ID: {webhook_result.get('visit_id')}")
        
        if webhook_result.get('error'):
            print(f"   Error: {webhook_result['error']}")
        
        # Test statistics
        print("\n📊 Testing capture statistics...")
        
        stats = await capture_service.get_capture_statistics(db)
        
        print(f"✅ Capture statistics:")
        print(f"   Total Captures: {stats.get('total_captures', 0)}")
        print(f"   Captures by Feeder: {stats.get('captures_by_feeder', {})}")
        print(f"   Captures by Day: {stats.get('captures_by_day', {})}")
        
        if stats.get('error'):
            print(f"   Error: {stats['error']}")
        
        print("\n🎉 Capture ingestion test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        # Cleanup test image
        if test_image_path.exists():
            test_image_path.unlink()
        if test_dir.exists() and not any(test_dir.iterdir()):
            test_dir.rmdir()

async def test_blue_iris_integration():
    """Test Blue Iris integration (if configured)"""
    print("\n🔗 Testing Blue Iris Integration")
    print("=" * 50)
    
    from app.services.blue_iris_integration import BlueIrisIntegration
    
    async with BlueIrisIntegration() as blue_iris:
        # Test connection
        print("Testing Blue Iris connection...")
        connection_result = await blue_iris.test_connection()
        
        print(f"✅ Connection test result:")
        print(f"   Connected: {connection_result['connected']}")
        print(f"   Response Time: {connection_result.get('response_time', 'N/A')}")
        
        if connection_result.get('error'):
            print(f"   Error: {connection_result['error']}")
            print("   Note: Blue Iris integration requires proper configuration")
        else:
            # Test getting cameras
            print("\nTesting camera retrieval...")
            cameras = await blue_iris.get_cameras()
            print(f"   Found {len(cameras)} cameras")
            
            # Test system status
            print("\nTesting system status...")
            status = await blue_iris.get_system_status()
            print(f"   System Status: {status}")

if __name__ == "__main__":
    print("🐦 Hummingbird Monitor - Capture Ingestion Test")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_capture_ingestion())
    asyncio.run(test_blue_iris_integration())
    
    print("\n✨ All tests completed!")
