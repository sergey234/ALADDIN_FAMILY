#!/usr/bin/env python3

print("🧪 Testing SFM Adapter...")

try:
    from sfm_adapter import sfm_adapter
    print("✅ SFM adapter import successful")

    # Test health check
    health = sfm_adapter.health_check()
    print(f"Health status: {health['status']}")
    print(f"SFM available: {health['sfm_available']}")

    # Test function execution
    success, result, error = sfm_adapter.execute_function('get_component_status', {'component_id': 'test'})
    status = "✅" if success else "❌"
    source = result.get('source') if success else str(error)
    print(f"Function test: {status} source: {source}")

    # Test multiple functions
    test_functions = [
        'get_phishing_sensitivity',
        'get_ai_categories_stats',
        'get_notifications_unread_count'
    ]

    print("\nTesting multiple functions:")
    for func in test_functions:
        success, result, error = sfm_adapter.execute_function(func, {})
        status = "✅" if success else "❌"
        source = result.get('source') if success else str(error)
        print(f"  {func}: {status} {source}")

    # Show metrics
    metrics = sfm_adapter.get_metrics()
    print(f"\n📊 Metrics: {metrics['total_calls']} calls")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("✅ Test completed!")


