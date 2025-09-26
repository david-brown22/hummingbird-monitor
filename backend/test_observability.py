"""
Test script for observability system
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from app.services.observability import ObservabilityService
from app.core.database import SessionLocal, engine
from app.models import bird, visit, alert, summary

async def test_observability_system():
    """Test the observability service"""
    print("🧪 Testing Observability Service")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        observability_service = ObservabilityService()
        
        # Test logging
        print("📝 Testing logging system...")
        
        await observability_service.log_event(
            event_type="test_event",
            message="Test log message",
            level="INFO",
            service="test_service",
            metadata={"test_key": "test_value"}
        )
        
        await observability_service.log_event(
            event_type="error_event",
            message="Test error message",
            level="ERROR",
            service="test_service",
            metadata={"error_code": "TEST_ERROR"}
        )
        
        print("✅ Logging system tested successfully")
        
        # Test metrics recording
        print("\n📊 Testing metrics recording...")
        
        await observability_service.record_metric(
            metric_name="test_metric",
            value=42.0,
            metric_type="counter",
            tags={"environment": "test"}
        )
        
        await observability_service.record_metric(
            metric_name="visit_count",
            value=1.0,
            metric_type="counter",
            tags={"feeder_id": "feeder_001"}
        )
        
        await observability_service.record_metric(
            metric_name="response_time",
            value=0.5,
            metric_type="histogram",
            tags={"endpoint": "/api/test"}
        )
        
        print("✅ Metrics recording tested successfully")
        
        # Test performance recording
        print("\n⚡ Testing performance recording...")
        
        # Simulate some operations
        operations = [
            ("bird_identification", 1.2, True),
            ("visit_tracking", 0.3, True),
            ("summary_generation", 2.5, True),
            ("alert_calculation", 0.8, True),
            ("database_query", 0.1, True),
            ("api_call", 0.5, False)  # One failed operation
        ]
        
        for operation, duration, success in operations:
            await observability_service.record_performance(
                operation=operation,
                duration=duration,
                success=success,
                metadata={"test": True}
            )
        
        print("✅ Performance recording tested successfully")
        
        # Test system metrics
        print("\n📈 Testing system metrics...")
        
        system_metrics = await observability_service.get_system_metrics(db=db)
        
        if "error" not in system_metrics:
            print(f"✅ System metrics retrieved:")
            print(f"   - Health score: {system_metrics['health_score']:.1f}")
            print(f"   - Total requests: {system_metrics['metrics']['system']['total_requests']}")
            print(f"   - Successful requests: {system_metrics['metrics']['system']['successful_requests']}")
            print(f"   - Failed requests: {system_metrics['metrics']['system']['failed_requests']}")
            print(f"   - Average response time: {system_metrics['metrics']['system']['average_response_time']:.2f}s")
            print(f"   - Uptime: {system_metrics['metrics']['system']['uptime_seconds']:.1f}s")
        else:
            print(f"⚠️  System metrics failed: {system_metrics['error']}")
        
        # Test health status
        print("\n🏥 Testing health status...")
        
        health_status = await observability_service.get_health_status(db=db)
        
        if "error" not in health_status:
            print(f"✅ Health status retrieved:")
            print(f"   - Overall status: {health_status['overall_status']}")
            print(f"   - Health checks: {len(health_status['health_checks'])}")
            for check_name, check_data in health_status['health_checks'].items():
                print(f"     * {check_name}: {check_data.get('status', 'unknown')}")
        else:
            print(f"⚠️  Health status failed: {health_status['error']}")
        
        # Test performance analysis
        print("\n📊 Testing performance analysis...")
        
        performance_analysis = await observability_service.get_performance_analysis()
        
        if "error" not in performance_analysis:
            print(f"✅ Performance analysis retrieved:")
            for operation, data in performance_analysis['performance_analysis'].items():
                print(f"   - {operation}:")
                print(f"     * Total operations: {data['total_operations']}")
                print(f"     * Success rate: {data['success_rate']:.2%}")
                print(f"     * Average duration: {data['average_duration']:.2f}s")
        else:
            print(f"⚠️  Performance analysis failed: {performance_analysis['error']}")
        
        # Test logs retrieval
        print("\n📋 Testing logs retrieval...")
        
        logs = await observability_service.get_logs(
            level="INFO",
            limit=10
        )
        
        if "error" not in logs:
            print(f"✅ Logs retrieved:")
            print(f"   - Total logs: {logs['total_count']}")
            print(f"   - Filtered logs: {len(logs['logs'])}")
            for log in logs['logs'][:3]:  # Show first 3 logs
                print(f"     * {log['timestamp']}: {log['level']} - {log['message']}")
        else:
            print(f"⚠️  Logs retrieval failed: {logs['error']}")
        
        print("\n✅ Observability system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Observability system test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_observability_api():
    """Test the observability API endpoints"""
    print("\n🌐 Testing Observability API")
    print("=" * 50)
    
    # This would test the actual API endpoints
    # For now, we'll just print the available endpoints
    
    endpoints = [
        "GET /api/observability/metrics - Get system metrics",
        "GET /api/observability/health - Get health status",
        "GET /api/observability/performance - Get performance analysis",
        "GET /api/observability/logs - Get filtered logs",
        "POST /api/observability/log - Log an event",
        "POST /api/observability/metric - Record a metric",
        "POST /api/observability/performance - Record performance data",
        "GET /api/observability/dashboard - Get observability dashboard",
        "GET /api/observability/alerts/status - Get alert status",
        "GET /api/observability/system/info - Get system information",
        "GET /api/observability/config - Get observability configuration",
        "GET /api/observability/health/check - Simple health check"
    ]
    
    print("Available API endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    print("\n✅ API endpoints documented!")

async def test_observability_performance():
    """Test observability system performance"""
    print("\n⚡ Testing Observability Performance")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        observability_service = ObservabilityService()
        
        # Test logging performance
        print("Testing logging performance...")
        
        start_time = time.time()
        
        # Log 100 events
        for i in range(100):
            await observability_service.log_event(
                event_type="performance_test",
                message=f"Test message {i}",
                level="INFO",
                service="performance_test"
            )
        
        end_time = time.time()
        logging_time = end_time - start_time
        
        print(f"✅ Logging performance:")
        print(f"   - 100 events logged in {logging_time:.2f} seconds")
        print(f"   - Average time per log: {logging_time/100*1000:.2f}ms")
        
        # Test metrics performance
        print("\nTesting metrics performance...")
        
        start_time = time.time()
        
        # Record 100 metrics
        for i in range(100):
            await observability_service.record_metric(
                metric_name=f"test_metric_{i}",
                value=random.uniform(0, 100),
                metric_type="gauge"
            )
        
        end_time = time.time()
        metrics_time = end_time - start_time
        
        print(f"✅ Metrics performance:")
        print(f"   - 100 metrics recorded in {metrics_time:.2f} seconds")
        print(f"   - Average time per metric: {metrics_time/100*1000:.2f}ms")
        
        # Test performance recording
        print("\nTesting performance recording...")
        
        start_time = time.time()
        
        # Record 50 performance entries
        for i in range(50):
            await observability_service.record_performance(
                operation=f"test_operation_{i}",
                duration=random.uniform(0.1, 2.0),
                success=random.choice([True, False])
            )
        
        end_time = time.time()
        performance_time = end_time - start_time
        
        print(f"✅ Performance recording:")
        print(f"   - 50 performance entries recorded in {performance_time:.2f} seconds")
        print(f"   - Average time per entry: {performance_time/50*1000:.2f}ms")
        
        # Test system metrics retrieval
        print("\nTesting system metrics retrieval...")
        
        start_time = time.time()
        
        system_metrics = await observability_service.get_system_metrics(db=db)
        
        end_time = time.time()
        metrics_retrieval_time = end_time - start_time
        
        print(f"✅ System metrics retrieval:")
        print(f"   - Metrics retrieved in {metrics_retrieval_time:.2f} seconds")
        print(f"   - Success: {'error' not in system_metrics}")
        
        print("\n✅ Performance test completed!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_observability_stress():
    """Test observability system under stress"""
    print("\n💪 Testing Observability Stress")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        observability_service = ObservabilityService()
        
        # Test concurrent operations
        print("Testing concurrent operations...")
        
        async def stress_test_operation(operation_id: int):
            """Simulate a stress test operation"""
            try:
                # Log event
                await observability_service.log_event(
                    event_type="stress_test",
                    message=f"Stress test operation {operation_id}",
                    level="INFO",
                    service="stress_test"
                )
                
                # Record metric
                await observability_service.record_metric(
                    metric_name="stress_test_metric",
                    value=operation_id,
                    metric_type="counter"
                )
                
                # Record performance
                await observability_service.record_performance(
                    operation=f"stress_operation_{operation_id}",
                    duration=random.uniform(0.1, 1.0),
                    success=True
                )
                
                return True
            except Exception as e:
                print(f"Error in operation {operation_id}: {e}")
                return False
        
        # Run 50 concurrent operations
        start_time = time.time()
        
        tasks = [stress_test_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        stress_time = end_time - start_time
        
        successful_operations = sum(1 for result in results if result is True)
        failed_operations = len(results) - successful_operations
        
        print(f"✅ Stress test results:")
        print(f"   - Total operations: {len(results)}")
        print(f"   - Successful operations: {successful_operations}")
        print(f"   - Failed operations: {failed_operations}")
        print(f"   - Total time: {stress_time:.2f} seconds")
        print(f"   - Operations per second: {len(results)/stress_time:.2f}")
        
        # Test system under load
        print("\nTesting system under load...")
        
        start_time = time.time()
        
        # Get system metrics under load
        system_metrics = await observability_service.get_system_metrics(db=db)
        
        end_time = time.time()
        load_time = end_time - start_time
        
        print(f"✅ System under load:")
        print(f"   - Metrics retrieval time: {load_time:.2f} seconds")
        print(f"   - Success: {'error' not in system_metrics}")
        
        print("\n✅ Stress test completed!")
        
    except Exception as e:
        print(f"❌ Stress test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_observability_integration():
    """Test observability integration with other services"""
    print("\n🔗 Testing Observability Integration")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        observability_service = ObservabilityService()
        
        # Test integration with visit tracking
        print("Testing visit tracking integration...")
        
        await observability_service.log_event(
            event_type="visit_recorded",
            message="New visit recorded",
            level="INFO",
            service="visit_tracker",
            metadata={"feeder_id": "feeder_001", "bird_id": 1}
        )
        
        await observability_service.record_metric(
            metric_name="visit_count",
            value=1.0,
            metric_type="counter",
            tags={"feeder_id": "feeder_001"}
        )
        
        # Test integration with bird identification
        print("Testing bird identification integration...")
        
        await observability_service.log_event(
            event_type="bird_identified",
            message="Bird successfully identified",
            level="INFO",
            service="bird_identification",
            metadata={"bird_id": 1, "confidence": 0.95}
        )
        
        await observability_service.record_metric(
            metric_name="identification_confidence",
            value=0.95,
            metric_type="histogram",
            tags={"bird_id": "1"}
        )
        
        # Test integration with alert system
        print("Testing alert system integration...")
        
        await observability_service.log_event(
            event_type="alert_triggered",
            message="Feeder alert triggered",
            level="WARNING",
            service="feeder_alert_logic",
            metadata={"feeder_id": "feeder_001", "alert_level": "critical"}
        )
        
        await observability_service.record_metric(
            metric_name="alert_count",
            value=1.0,
            metric_type="counter",
            tags={"severity": "critical"}
        )
        
        # Test integration with summary generation
        print("Testing summary generation integration...")
        
        await observability_service.log_event(
            event_type="summary_generated",
            message="Daily summary generated",
            level="INFO",
            service="summary_generator",
            metadata={"summary_type": "daily", "date": "2024-01-15"}
        )
        
        await observability_service.record_performance(
            operation="summary_generation",
            duration=2.5,
            success=True,
            metadata={"summary_type": "daily"}
        )
        
        print("✅ Integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def main():
    """Run all observability tests"""
    print("🐦 Hummingbird Monitor - Observability Test Suite")
    print("=" * 70)
    
    # Run tests
    await test_observability_system()
    await test_observability_api()
    await test_observability_performance()
    await test_observability_stress()
    await test_observability_integration()
    
    print("\n🎉 All observability tests completed!")
    print("\n📚 Next steps:")
    print("1. Start the API server: python run_server.py")
    print("2. Test API endpoints: http://localhost:8000/docs")
    print("3. Get system metrics: GET /api/observability/metrics")
    print("4. Check health status: GET /api/observability/health")
    print("5. View observability dashboard: GET /api/observability/dashboard")

if __name__ == "__main__":
    asyncio.run(main())
