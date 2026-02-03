#!/usr/bin/env python3
"""
SIMPLE COMPLETE 108 ENDPOINT TEST
Тестируем все 108 эндпоинтов ALADDIN API
"""

import requests
import json
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_endpoints():
    """Get all endpoints from API Gateway"""
    try:
        with open('api_gateway_current.py', 'r') as f:
            content = f.read()

        pattern = r'@app\.(get|post|put|delete)\("([^"]+)"\)'
        matches = re.findall(pattern, content)

        endpoints = []
        for method, path in matches:
            if path.startswith('/api/'):
                endpoints.append(path)

        return list(set(endpoints))
    except:
        return []

def test_endpoint(endpoint):
    """Test single endpoint"""
    start_time = time.time()
    url = f"http://149.154.65.180:8002{endpoint}"

    try:
        response = requests.get(url, timeout=10)
        response_time = (time.time() - start_time) * 1000

        success = response.status_code == 200
        has_real_data = False

        if success:
            try:
                data = response.json()
                source = data.get('source', '')
                has_real_data = 'sfm_real' in source or 'protection' in source
            except:
                pass

        return {
            'endpoint': endpoint,
            'success': success,
            'has_real_data': has_real_data,
            'response_time': round(response_time, 2),
            'status_code': response.status_code
        }
    except:
        response_time = (time.time() - start_time) * 1000
        return {
            'endpoint': endpoint,
            'success': False,
            'has_real_data': False,
            'response_time': round(response_time, 2),
            'status_code': None
        }

def main():
    print("🚀 ALADDIN COMPLETE 108 ENDPOINT TEST")
    print("=" * 60)

    endpoints = get_endpoints()
    print(f"Found {len(endpoints)} endpoints to test")

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_endpoint, ep) for ep in endpoints]

        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)

            progress = (i + 1) / len(endpoints) * 100
            status = "✅" if result['success'] and result['has_real_data'] else "⚠️" if result['success'] else "❌"
            print(f"[{progress:.1f}%] {status} {result['endpoint']} ({result['response_time']}ms)")

    # Calculate statistics
    successful = sum(1 for r in results if r['success'])
    real_data = sum(1 for r in results if r['has_real_data'])
    response_times = [r['response_time'] for r in results if r['success']]

    success_rate = successful / len(endpoints) * 100
    real_data_rate = real_data / len(endpoints) * 100

    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
    else:
        avg_time = max_time = 0

    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Total endpoints: {len(endpoints)}")
    print(f"Successful: {successful}")
    print(f"Real protection data: {real_data}")
    print(".1f")
    print(".1f")
    print(".1f")
    print(".1f")

    production_ready = success_rate >= 95 and real_data_rate >= 50 and avg_time < 1000

    if production_ready:
        print("\n✅ PRODUCTION READY!")
    else:
        print("\n⚠️ NEEDS WORK")

    return production_ready

if __name__ == "__main__":
    main()