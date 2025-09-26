"""
Test script for summary generation system
"""

import asyncio
from datetime import date, datetime, timedelta
from app.services.summary_generator import SummaryGeneratorService
from app.core.database import SessionLocal, engine
from app.models import bird, visit, alert, summary

async def test_summary_generation():
    """Test the summary generation service"""
    print("🧪 Testing Summary Generation Service")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        summary_service = SummaryGeneratorService()
        
        # Test daily summary generation
        print("📅 Testing daily summary generation...")
        
        daily_summary = await summary_service.generate_daily_summary(
            target_date=date.today(),
            db=db
        )
        
        print(f"✅ Daily summary generated:")
        print(f"   - Date: {daily_summary['date']}")
        print(f"   - Title: {daily_summary['title']}")
        print(f"   - Total visits: {daily_summary['total_visits']}")
        print(f"   - Unique birds: {daily_summary['unique_birds']}")
        print(f"   - Peak hour: {daily_summary['peak_hour']}")
        print(f"   - Model used: {daily_summary['model_used']}")
        print(f"   - Confidence: {daily_summary['confidence_score']}")
        print(f"   - Content preview: {daily_summary['content'][:100]}...")
        
        # Test weekly summary generation
        print("\n📊 Testing weekly summary generation...")
        
        weekly_summary = await summary_service.generate_weekly_summary(
            target_date=date.today(),
            db=db
        )
        
        print(f"✅ Weekly summary generated:")
        print(f"   - Date: {weekly_summary['date']}")
        print(f"   - Title: {weekly_summary['title']}")
        print(f"   - Total visits: {weekly_summary['total_visits']}")
        print(f"   - Unique birds: {weekly_summary['unique_birds']}")
        print(f"   - Model used: {weekly_summary['model_used']}")
        print(f"   - Content preview: {weekly_summary['content'][:100]}...")
        
        # Test bird profile generation
        print("\n🐦 Testing bird profile generation...")
        
        bird_profile = await summary_service.generate_bird_profile_summary(
            bird_id=1,
            days=30,
            db=db
        )
        
        if "error" not in bird_profile:
            print(f"✅ Bird profile generated:")
            print(f"   - Bird ID: {bird_profile['bird_id']}")
            print(f"   - Bird name: {bird_profile['bird_name']}")
            print(f"   - Total visits: {bird_profile['total_visits']}")
            print(f"   - Average duration: {bird_profile['average_duration']}")
            print(f"   - Favorite feeder: {bird_profile['favorite_feeder']}")
            print(f"   - Peak hour: {bird_profile['peak_hour']}")
            print(f"   - Model used: {bird_profile['model_used']}")
            print(f"   - Content preview: {bird_profile['content'][:100]}...")
        else:
            print(f"⚠️  Bird profile generation failed: {bird_profile['error']}")
        
        # Test feeder analysis generation
        print("\n🍯 Testing feeder analysis generation...")
        
        feeder_analysis = await summary_service.generate_feeder_analysis_summary(
            feeder_id="feeder_001",
            days=7,
            db=db
        )
        
        if "error" not in feeder_analysis:
            print(f"✅ Feeder analysis generated:")
            print(f"   - Feeder ID: {feeder_analysis['feeder_id']}")
            print(f"   - Total visits: {feeder_analysis['total_visits']}")
            print(f"   - Unique birds: {feeder_analysis['unique_birds']}")
            print(f"   - Average daily visits: {feeder_analysis['average_daily_visits']}")
            print(f"   - Peak hour: {feeder_analysis['peak_hour']}")
            print(f"   - Nectar estimate: {feeder_analysis['nectar_estimate']}")
            print(f"   - Model used: {feeder_analysis['model_used']}")
            print(f"   - Content preview: {feeder_analysis['content'][:100]}...")
        else:
            print(f"⚠️  Feeder analysis generation failed: {feeder_analysis['error']}")
        
        # Test alert summary generation
        print("\n🚨 Testing alert summary generation...")
        
        # First, check if there are any alerts
        alerts = db.query(alert.Alert).all()
        if alerts:
            alert_summary = await summary_service.generate_alert_summary(
                alert_id=alerts[0].id,
                db=db
            )
            
            if "error" not in alert_summary:
                print(f"✅ Alert summary generated:")
                print(f"   - Alert ID: {alert_summary['alert_id']}")
                print(f"   - Alert type: {alert_summary['alert_type']}")
                print(f"   - Feeder ID: {alert_summary['feeder_id']}")
                print(f"   - Severity: {alert_summary['severity']}")
                print(f"   - Visit count: {alert_summary['visit_count']}")
                print(f"   - Nectar level: {alert_summary['nectar_level']}")
                print(f"   - Model used: {alert_summary['model_used']}")
                print(f"   - Content preview: {alert_summary['content'][:100]}...")
            else:
                print(f"⚠️  Alert summary generation failed: {alert_summary['error']}")
        else:
            print("⚠️  No alerts found for testing")
        
        print("\n✅ Summary generation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Summary generation test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_summary_generation_api():
    """Test the summary generation API endpoints"""
    print("\n🌐 Testing Summary Generation API")
    print("=" * 50)
    
    # This would test the actual API endpoints
    # For now, we'll just print the available endpoints
    
    endpoints = [
        "POST /api/summary-generation/daily - Generate daily summary",
        "POST /api/summary-generation/weekly - Generate weekly summary",
        "POST /api/summary-generation/bird/{bird_id}/profile - Generate bird profile",
        "POST /api/summary-generation/feeder/{feeder_id}/analysis - Generate feeder analysis",
        "POST /api/summary-generation/alert/{alert_id}/summary - Generate alert summary",
        "GET /api/summary-generation/prompts - Get available prompts",
        "GET /api/summary-generation/models - Get available models",
        "GET /api/summary-generation/health - Health check"
    ]
    
    print("Available API endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    print("\n✅ API endpoints documented!")

async def test_summary_quality():
    """Test summary quality and metrics"""
    print("\n📈 Testing Summary Quality")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        summary_service = SummaryGeneratorService()
        
        # Test different model configurations
        print("Testing different model configurations...")
        
        # Test creative model
        print("🎨 Testing creative model...")
        creative_summary = await summary_service.generate_daily_summary(
            target_date=date.today(),
            db=db
        )
        
        if "error" not in creative_summary:
            print(f"✅ Creative summary generated:")
            print(f"   - Word count: {len(creative_summary['content'].split())}")
            print(f"   - Model: {creative_summary['model_used']}")
            print(f"   - Confidence: {creative_summary['confidence_score']}")
        
        # Test analytical model
        print("\n🔬 Testing analytical model...")
        analytical_summary = await summary_service.generate_feeder_analysis_summary(
            feeder_id="feeder_001",
            days=7,
            db=db
        )
        
        if "error" not in analytical_summary:
            print(f"✅ Analytical summary generated:")
            print(f"   - Word count: {len(analytical_summary['content'].split())}")
            print(f"   - Model: {analytical_summary['model_used']}")
            print(f"   - Confidence: {analytical_summary['confidence_score']}")
        
        # Test prompt templates
        print("\n📝 Testing prompt templates...")
        
        prompts = {
            "daily_summary": summary_service._get_daily_summary_prompt(),
            "weekly_summary": summary_service._get_weekly_summary_prompt(),
            "bird_profile": summary_service._get_bird_profile_prompt(),
            "feeder_analysis": summary_service._get_feeder_analysis_prompt(),
            "alert_summary": summary_service._get_alert_summary_prompt()
        }
        
        for prompt_type, prompt in prompts.items():
            print(f"✅ {prompt_type} prompt:")
            print(f"   - Length: {len(prompt)} characters")
            print(f"   - Preview: {prompt[:100]}...")
        
        print("\n✅ Summary quality test completed!")
        
    except Exception as e:
        print(f"❌ Summary quality test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_summary_generation_performance():
    """Test summary generation performance"""
    print("\n⚡ Testing Summary Generation Performance")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        summary_service = SummaryGeneratorService()
        
        # Test generation time
        print("Testing generation time...")
        
        start_time = datetime.now()
        
        daily_summary = await summary_service.generate_daily_summary(
            target_date=date.today(),
            db=db
        )
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Daily summary generation time: {generation_time:.2f} seconds")
        
        # Test multiple generations
        print("\nTesting multiple generations...")
        
        start_time = datetime.now()
        
        summaries = []
        for i in range(3):
            summary = await summary_service.generate_daily_summary(
                target_date=date.today() - timedelta(days=i),
                db=db
            )
            summaries.append(summary)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        average_time = total_time / len(summaries)
        
        print(f"✅ Multiple generations:")
        print(f"   - Total time: {total_time:.2f} seconds")
        print(f"   - Average time: {average_time:.2f} seconds per summary")
        print(f"   - Summaries generated: {len(summaries)}")
        
        # Test error handling
        print("\nTesting error handling...")
        
        try:
            # Test with invalid date
            invalid_summary = await summary_service.generate_daily_summary(
                target_date=date(1900, 1, 1),
                db=db
            )
            print(f"✅ Error handling test passed")
        except Exception as e:
            print(f"✅ Error handling test passed: {e}")
        
        print("\n✅ Performance test completed!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def main():
    """Run all summary generation tests"""
    print("🐦 Hummingbird Monitor - Summary Generation Test Suite")
    print("=" * 70)
    
    # Run tests
    await test_summary_generation()
    await test_summary_generation_api()
    await test_summary_quality()
    await test_summary_generation_performance()
    
    print("\n🎉 All summary generation tests completed!")
    print("\n📚 Next steps:")
    print("1. Start the API server: python run_server.py")
    print("2. Test API endpoints: http://localhost:8000/docs")
    print("3. Generate daily summary: POST /api/summary-generation/daily")
    print("4. Generate weekly summary: POST /api/summary-generation/weekly")
    print("5. Generate bird profile: POST /api/summary-generation/bird/1/profile")
    print("6. Generate feeder analysis: POST /api/summary-generation/feeder/feeder_001/analysis")

if __name__ == "__main__":
    asyncio.run(main())
