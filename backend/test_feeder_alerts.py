"""
Test script for feeder alert logic system
"""

import asyncio
from datetime import datetime, date, timedelta
from app.services.feeder_alert_logic import FeederAlertLogicService
from app.core.database import SessionLocal, engine
from app.models import bird, visit, alert, summary

async def test_feeder_alert_logic():
    """Test the feeder alert logic service"""
    print("🧪 Testing Feeder Alert Logic Service")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        alert_service = FeederAlertLogicService()
        
        # Test nectar depletion calculation
        print("🍯 Testing nectar depletion calculation...")
        
        depletion_analysis = await alert_service.calculate_nectar_depletion(
            feeder_id="feeder_001",
            days=7,
            db=db
        )
        
        if "error" not in depletion_analysis:
            print(f"✅ Nectar depletion analysis:")
            print(f"   - Feeder ID: {depletion_analysis['feeder_id']}")
            print(f"   - Total visits: {depletion_analysis['total_visits']}")
            print(f"   - Weighted visits: {depletion_analysis['weighted_visits']}")
            print(f"   - Estimated depletion: {depletion_analysis['estimated_depletion']}ml")
            print(f"   - Remaining nectar: {depletion_analysis['remaining_nectar']}ml")
            print(f"   - Depletion percentage: {depletion_analysis['depletion_percentage']:.1f}%")
            print(f"   - Alert level: {depletion_analysis['alert_level']}")
            print(f"   - Days until empty: {depletion_analysis['days_until_empty']}")
            print(f"   - Seasonal factor: {depletion_analysis['seasonal_factor']}")
            print(f"   - Recommendations: {len(depletion_analysis['recommendations'])}")
        else:
            print(f"⚠️  Nectar depletion calculation failed: {depletion_analysis['error']}")
        
        # Test alert condition checking
        print("\n🚨 Testing alert condition checking...")
        
        alert_status = await alert_service.check_alert_conditions(
            feeder_id="feeder_001",
            db=db
        )
        
        if "error" not in alert_status:
            print(f"✅ Alert status check:")
            print(f"   - Alert created: {alert_status['alert_created']}")
            print(f"   - Alert ID: {alert_status.get('alert_id', 'N/A')}")
            print(f"   - Severity: {alert_status.get('severity', 'N/A')}")
            print(f"   - Message: {alert_status.get('message', 'N/A')}")
            print(f"   - Existing alerts: {alert_status['existing_alerts']}")
        else:
            print(f"⚠️  Alert condition check failed: {alert_status['error']}")
        
        # Test alert history
        print("\n📊 Testing alert history...")
        
        alert_history = await alert_service.get_feeder_alert_history(
            feeder_id="feeder_001",
            days=30,
            db=db
        )
        
        if "error" not in alert_history:
            print(f"✅ Alert history:")
            print(f"   - Feeder ID: {alert_history['feeder_id']}")
            print(f"   - Total alerts: {alert_history['total_alerts']}")
            print(f"   - Active alerts: {alert_history['active_alerts']}")
            print(f"   - Alert frequency: {alert_history['alert_frequency']:.2f} alerts/day")
            print(f"   - Severity breakdown: {alert_history['severity_breakdown']}")
        else:
            print(f"⚠️  Alert history retrieval failed: {alert_history['error']}")
        
        # Test feeder prediction
        print("\n🔮 Testing feeder prediction...")
        
        prediction = await alert_service.predict_feeder_needs(
            feeder_id="feeder_001",
            days_ahead=7,
            db=db
        )
        
        if "error" not in prediction:
            print(f"✅ Feeder prediction:")
            print(f"   - Feeder ID: {prediction['feeder_id']}")
            print(f"   - Days ahead: {prediction['prediction_period']['days_ahead']}")
            print(f"   - Predicted depletion: {prediction['predicted_depletion']}ml")
            print(f"   - Predicted remaining: {prediction['predicted_remaining']}ml")
            print(f"   - Confidence score: {prediction['confidence_score']:.2f}")
            print(f"   - Predicted alerts: {len(prediction['predicted_alerts'])}")
            print(f"   - Recommendations: {len(prediction['recommendations'])}")
        else:
            print(f"⚠️  Feeder prediction failed: {prediction['error']}")
        
        # Test system alert overview
        print("\n🌐 Testing system alert overview...")
        
        system_overview = await alert_service.get_system_alert_overview(db=db)
        
        if "error" not in system_overview:
            print(f"✅ System alert overview:")
            print(f"   - System health score: {system_overview['system_health']['score']:.1f}")
            print(f"   - System status: {system_overview['system_health']['status']}")
            print(f"   - Total alerts: {system_overview['alert_summary']['total']}")
            print(f"   - Critical alerts: {system_overview['alert_summary']['critical']}")
            print(f"   - Warning alerts: {system_overview['alert_summary']['warning']}")
            print(f"   - Info alerts: {system_overview['alert_summary']['info']}")
            print(f"   - Feeder count: {system_overview['feeder_count']}")
            print(f"   - Feeder statuses: {len(system_overview['feeder_statuses'])}")
        else:
            print(f"⚠️  System overview failed: {system_overview['error']}")
        
        print("\n✅ Feeder alert logic test completed successfully!")
        
    except Exception as e:
        print(f"❌ Feeder alert logic test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_feeder_alert_api():
    """Test the feeder alert API endpoints"""
    print("\n🌐 Testing Feeder Alert API")
    print("=" * 50)
    
    # This would test the actual API endpoints
    # For now, we'll just print the available endpoints
    
    endpoints = [
        "GET /api/feeder-alerts/feeder/{feeder_id}/depletion - Calculate nectar depletion",
        "POST /api/feeder-alerts/feeder/{feeder_id}/check-alerts - Check alert conditions",
        "GET /api/feeder-alerts/feeder/{feeder_id}/history - Get alert history",
        "GET /api/feeder-alerts/feeder/{feeder_id}/predict - Predict feeder needs",
        "GET /api/feeder-alerts/system/overview - Get system alert overview",
        "POST /api/feeder-alerts/feeder/{feeder_id}/refill - Mark feeder as refilled",
        "GET /api/feeder-alerts/alerts/active - Get active alerts",
        "GET /api/feeder-alerts/health - Health check"
    ]
    
    print("Available API endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    print("\n✅ API endpoints documented!")

async def test_alert_configuration():
    """Test alert configuration and thresholds"""
    print("\n⚙️ Testing Alert Configuration")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        alert_service = FeederAlertLogicService()
        
        # Test default configuration
        print("Testing default configuration...")
        print(f"✅ Default nectar capacity: {alert_service.default_nectar_capacity}ml")
        print(f"✅ Default depletion rate: {alert_service.default_depletion_rate}ml/visit")
        print(f"✅ Alert thresholds: {alert_service.alert_thresholds}")
        print(f"✅ Visit weight factors: {alert_service.visit_weight_factors}")
        print(f"✅ Seasonal adjustments: {alert_service.seasonal_adjustments}")
        
        # Test seasonal factor calculation
        print("\nTesting seasonal factor calculation...")
        current_season = alert_service._get_seasonal_factor()
        print(f"✅ Current seasonal factor: {current_season}")
        
        # Test alert level determination
        print("\nTesting alert level determination...")
        test_levels = [5.0, 15.0, 30.0, 60.0, 90.0]
        for level in test_levels:
            alert_level = alert_service._determine_alert_level(level)
            print(f"   - {level}ml remaining → {alert_level} alert")
        
        # Test visit weight calculation
        print("\nTesting visit weight calculation...")
        from app.models.visit import Visit
        
        # Create a test visit
        test_visit = Visit(
            feeder_id="test_feeder",
            camera_id="test_camera",
            visit_time=datetime.utcnow(),
            duration_seconds=25.0,
            confidence_score=0.85,
            temperature=75.0,
            weather_condition="sunny"
        )
        
        weight = alert_service._calculate_visit_weight(test_visit)
        print(f"✅ Test visit weight: {weight:.2f}")
        
        print("\n✅ Alert configuration test completed!")
        
    except Exception as e:
        print(f"❌ Alert configuration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_alert_scenarios():
    """Test different alert scenarios"""
    print("\n🎭 Testing Alert Scenarios")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        alert_service = FeederAlertLogicService()
        
        # Test different feeder scenarios
        test_feeders = [
            {"id": "feeder_001", "description": "Normal usage feeder"},
            {"id": "feeder_002", "description": "High usage feeder"},
            {"id": "feeder_003", "description": "Low usage feeder"},
            {"id": "feeder_004", "description": "New feeder"}
        ]
        
        for feeder in test_feeders:
            print(f"\nTesting {feeder['description']} ({feeder['id']})...")
            
            # Calculate depletion
            depletion = await alert_service.calculate_nectar_depletion(
                feeder_id=feeder["id"],
                days=7,
                db=db
            )
            
            if "error" not in depletion:
                print(f"   - Alert level: {depletion['alert_level']}")
                print(f"   - Remaining nectar: {depletion['remaining_nectar']}ml")
                print(f"   - Days until empty: {depletion['days_until_empty']}")
                print(f"   - Recommendations: {len(depletion['recommendations'])}")
            else:
                print(f"   - Error: {depletion['error']}")
        
        # Test prediction scenarios
        print("\nTesting prediction scenarios...")
        
        prediction_scenarios = [3, 7, 14, 30]
        for days in prediction_scenarios:
            prediction = await alert_service.predict_feeder_needs(
                feeder_id="feeder_001",
                days_ahead=days,
                db=db
            )
            
            if "error" not in prediction:
                print(f"   - {days} days ahead:")
                print(f"     * Predicted remaining: {prediction['predicted_remaining']}ml")
                print(f"     * Confidence score: {prediction['confidence_score']:.2f}")
                print(f"     * Predicted alerts: {len(prediction['predicted_alerts'])}")
            else:
                print(f"   - {days} days ahead: Error - {prediction['error']}")
        
        print("\n✅ Alert scenarios test completed!")
        
    except Exception as e:
        print(f"❌ Alert scenarios test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_alert_performance():
    """Test alert system performance"""
    print("\n⚡ Testing Alert System Performance")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        alert_service = FeederAlertLogicService()
        
        # Test calculation speed
        print("Testing calculation speed...")
        
        start_time = datetime.now()
        
        # Test multiple feeder calculations
        feeders = ["feeder_001", "feeder_002", "feeder_003"]
        results = []
        
        for feeder_id in feeders:
            result = await alert_service.calculate_nectar_depletion(
                feeder_id=feeder_id,
                days=7,
                db=db
            )
            results.append(result)
        
        end_time = datetime.now()
        calculation_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Calculation performance:")
        print(f"   - Feeders processed: {len(feeders)}")
        print(f"   - Total time: {calculation_time:.2f} seconds")
        print(f"   - Average time per feeder: {calculation_time/len(feeders):.2f} seconds")
        
        # Test prediction speed
        print("\nTesting prediction speed...")
        
        start_time = datetime.now()
        
        prediction = await alert_service.predict_feeder_needs(
            feeder_id="feeder_001",
            days_ahead=7,
            db=db
        )
        
        end_time = datetime.now()
        prediction_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Prediction performance:")
        print(f"   - Prediction time: {prediction_time:.2f} seconds")
        print(f"   - Success: {'error' not in prediction}")
        
        # Test system overview speed
        print("\nTesting system overview speed...")
        
        start_time = datetime.now()
        
        overview = await alert_service.get_system_alert_overview(db=db)
        
        end_time = datetime.now()
        overview_time = (end_time - start_time).total_seconds()
        
        print(f"✅ System overview performance:")
        print(f"   - Overview time: {overview_time:.2f} seconds")
        print(f"   - Success: {'error' not in overview}")
        
        print("\n✅ Performance test completed!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def main():
    """Run all feeder alert tests"""
    print("🐦 Hummingbird Monitor - Feeder Alert Logic Test Suite")
    print("=" * 70)
    
    # Run tests
    await test_feeder_alert_logic()
    await test_feeder_alert_api()
    await test_alert_configuration()
    await test_alert_scenarios()
    await test_alert_performance()
    
    print("\n🎉 All feeder alert tests completed!")
    print("\n📚 Next steps:")
    print("1. Start the API server: python run_server.py")
    print("2. Test API endpoints: http://localhost:8000/docs")
    print("3. Calculate depletion: GET /api/feeder-alerts/feeder/feeder_001/depletion")
    print("4. Check alerts: POST /api/feeder-alerts/feeder/feeder_001/check-alerts")
    print("5. Get system overview: GET /api/feeder-alerts/system/overview")

if __name__ == "__main__":
    asyncio.run(main())
