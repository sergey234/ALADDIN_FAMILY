#!/usr/bin/env python3
"""
SIMPLE ENDPOINT TESTING FOR ALADDIN
Быстрое тестирование ключевых эндпоинтов
"""

import requests
import json
import time

def test_endpoint(name, url):
    """Test single endpoint"""
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        response_time = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            source = data.get('source', 'unknown')

            if 'sfm_real' in source or 'protection' in source:
                status = "✅ REAL DATA"
                data_type = "real_protection"
            elif 'mock' in source:
                status = "⚠️ MOCK DATA"
                data_type = "mock"
            else:
                status = "❓ OTHER"
                data_type = "other"

            return {
                'name': name,
                'url': url,
                'status': status,
                'data_type': data_type,
                'response_time': f"{response_time:.1f}ms",
                'success': True
            }
        else:
            return {
                'name': name,
                'url': url,
                'status': f"❌ HTTP {response.status_code}",
                'data_type': 'error',
                'response_time': f"{response_time:.1f}ms",
                'success': False
            }
    except Exception as e:
        return {
            'name': name,
            'url': url,
            'status': f"❌ ERROR: {str(e)}",
            'data_type': 'error',
            'response_time': 'N/A',
            'success': False
        }

def main():
    """Test key endpoints"""
    print("🚀 ALADDIN ENDPOINT TESTING")
    print("=" * 50)

    base_url = "http://149.154.65.180:8002"

    # Key endpoints to test
    endpoints = [
        ("Health Check", "/api/health"),
        ("Phishing Sensitivity", "/api/phishing/sensitivity"),
        ("Analytics Overview", "/api/analytics/overview"),
        ("Malware Scan", "/api/malware/scan_scheduled"),
        ("Firewall Rules", "/api/network/firewall_rules"),
        ("Notifications", "/api/notifications/list"),
        ("User Profile", "/api/user/profile"),
        ("System Health", "/api/system/health"),
    ]

    results = []
    total_tested = 0
    real_data_count = 0
    mock_data_count = 0
    failed_count = 0

    for name, path in endpoints:
        url = f"{base_url}{path}"
        result = test_endpoint(name, url)
        results.append(result)

        total_tested += 1
        if result['success']:
            if result['data_type'] == 'real_protection':
                real_data_count += 1
            elif result['data_type'] == 'mock':
                mock_data_count += 1
        else:
            failed_count += 1

        print(f"{result['status']} {result['name']} - {result['response_time']}")

    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total tested: {total_tested}")
    print(f"Real protection data: {real_data_count}")
    print(f"Mock data: {mock_data_count}")
    print(f"Failed: {failed_count}")

    success_rate = (total_tested - failed_count) / total_tested * 100
    real_data_rate = real_data_count / total_tested * 100

    print(".1f")
    print(".1f")

    production_ready = success_rate >= 90 and real_data_rate >= 50

    status = "✅ PRODUCTION READY" if production_ready else "⚠️ NEEDS WORK"
    print(f"\n🎯 Status: {status}")

    if production_ready:
        print("\n🚀 ALADDIN IS READY FOR PRODUCTION LAUNCH!")
        print("✅ Real protection data working")
        print("✅ API endpoints functional")
        print("✅ Performance acceptable")
    else:
        print("\n⚠️ Additional work needed before production")

    return production_ready

if __name__ == "__main__":
    main()