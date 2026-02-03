#!/usr/bin/env python3
"""
ALADDIN MOBILE APP INTEGRATION TESTING
Симуляция запросов от мобильного приложения к API
"""

import requests
import json
import time

def simulate_mobile_app_requests():
    """Simulate typical mobile app API calls"""

    base_url = "http://149.154.65.180:8002"

    # Typical mobile app request sequence
    mobile_requests = [
        # 1. App startup - check system health
        {"endpoint": "/api/health", "method": "GET", "description": "App startup health check"},

        # 2. Load main dashboard data
        {"endpoint": "/api/phishing/sensitivity", "method": "GET", "description": "Load phishing protection status"},
        {"endpoint": "/api/analytics/overview", "method": "GET", "description": "Load security analytics"},
        {"endpoint": "/api/system/health", "method": "GET", "description": "Load system health status"},

        # 3. Background sync requests (what app does periodically)
        {"endpoint": "/api/phishing/sensitivity", "method": "GET", "description": "Background phishing sync"},
        {"endpoint": "/api/analytics/overview?period=day", "method": "GET", "description": "Daily analytics sync"},
        {"endpoint": "/api/system/health", "method": "GET", "description": "System health monitoring"},

        # 4. User interaction requests
        {"endpoint": "/api/phishing/sensitivity", "method": "GET", "description": "User checks protection settings"},
    ]

    print("📱 ALADDIN MOBILE APP INTEGRATION TEST")
    print("=" * 60)
    print("Simulating typical mobile app API usage patterns...")

    results = []
    session = requests.Session()

    for i, req in enumerate(mobile_requests, 1):
        start_time = time.time()
        url = f"{base_url}{req['endpoint']}"

        try:
            if req['method'] == 'GET':
                response = session.get(url, timeout=10)
            else:
                response = session.post(url, json={}, timeout=10)

            response_time = (time.time() - start_time) * 1000

            result = {
                'request_num': i,
                'description': req['description'],
                'endpoint': req['endpoint'],
                'method': req['method'],
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200
            }

            if response.status_code == 200:
                try:
                    data = response.json()
                    result['data_size'] = len(json.dumps(data))
                    result['has_real_data'] = 'sfm_real' in json.dumps(data).lower() or 'protection' in json.dumps(data).lower()
                except:
                    result['data_size'] = len(response.text)
                    result['has_real_data'] = False
            else:
                result['data_size'] = 0
                result['has_real_data'] = False

            results.append(result)

            status_icon = "✅" if result['success'] and result['has_real_data'] else "⚠️" if result['success'] else "❌"
            print(f"{status_icon} {i}. {req['description']}")
            print(f"   {req['method']} {req['endpoint']} - {response.status_code} ({result['response_time_ms']}ms)")

        except Exception as e:
            results.append({
                'request_num': i,
                'description': req['description'],
                'endpoint': req['endpoint'],
                'method': req['method'],
                'status_code': None,
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'success': False,
                'error': str(e)
            })
            print(f"❌ {i}. {req['description']} - ERROR: {e}")

    # Analyze results
    print("\n" + "=" * 60)
    print("📊 MOBILE APP INTEGRATION ANALYSIS")

    successful_requests = sum(1 for r in results if r['success'])
    real_data_requests = sum(1 for r in results if r.get('has_real_data', False))
    avg_response_time = sum(r['response_time_ms'] for r in results if r['success']) / successful_requests if successful_requests > 0 else 0

    print(f"Total requests: {len(results)}")
    print(f"Successful: {successful_requests}/{len(results)} ({successful_requests/len(results)*100:.1f}%)")
    print(f"Real protection data: {real_data_requests}/{len(results)} ({real_data_requests/len(results)*100:.1f}%)")
    print(f"Average response time: {avg_response_time:.1f}ms")

    # Mobile app compatibility criteria
    mobile_ready = (
        successful_requests / len(results) >= 0.95 and  # 95% success rate
        avg_response_time < 1000 and  # < 1 second average
        real_data_requests > 0  # At least some real data
    )

    if mobile_ready:
        print("\n✅ MOBILE APP COMPATIBILITY: EXCELLENT")
        print("   • High success rate")
        print("   • Fast response times")
        print("   • Real protection data available")
        print("   • Ready for mobile app deployment")
        return True
    else:
        print("\n⚠️ MOBILE APP COMPATIBILITY: ISSUES DETECTED")
        if successful_requests / len(results) < 0.95:
            print("   • Low success rate - needs fixing")
        if avg_response_time >= 1000:
            print("   • Slow response times - needs optimization")
        if real_data_requests == 0:
            print("   • No real protection data - critical issue")
        return False

def test_api_stability():
    """Test API stability over time"""
    print("\n🧪 API STABILITY TEST (60 seconds)")

    base_url = "http://149.154.65.180:8002"
    start_time = time.time()
    request_count = 0
    success_count = 0

    while time.time() - start_time < 60:  # Test for 60 seconds
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            request_count += 1
            if response.status_code == 200:
                success_count += 1
        except:
            request_count += 1
        time.sleep(1)  # 1 request per second

    uptime = success_count / request_count * 100 if request_count > 0 else 0
    print(f"Requests: {request_count} | Successful: {success_count} | Uptime: {uptime:.1f}%")

    return uptime >= 95  # 95% uptime required

if __name__ == "__main__":
    # Run mobile app integration test
    mobile_test_passed = simulate_mobile_app_requests()

    # Run stability test
    stability_test_passed = test_api_stability()

    print("\n" + "=" * 60)
    print("🎯 FINAL MOBILE APP TEST RESULTS")

    if mobile_test_passed and stability_test_passed:
        print("✅ MOBILE APP INTEGRATION: FULLY COMPATIBLE")
        print("✅ API STABILITY: EXCELLENT")
        print("✅ READY FOR MOBILE APP DEPLOYMENT")
        exit(0)
    else:
        print("⚠️ MOBILE APP INTEGRATION: ISSUES DETECTED")
        if not mobile_test_passed:
            print("   • API compatibility issues")
        if not stability_test_passed:
            print("   • Stability issues detected")
        exit(1)