#!/usr/bin/env python3
"""
ALADDIN PERFORMANCE LOAD TESTING
Тестирование производительности API под нагрузкой
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_test_endpoint(url, requests_count=50):
    """Load test single endpoint"""
    response_times = []

    for i in range(requests_count):
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            end = time.time()

            if response.status_code == 200:
                response_times.append((end - start) * 1000)  # ms
        except:
            pass

    if response_times:
        return {
            'url': url,
            'total_requests': len(response_times),
            'avg_time': round(statistics.mean(response_times), 2),
            'min_time': round(min(response_times), 2),
            'max_time': round(max(response_times), 2),
            'p95_time': round(statistics.quantiles(response_times, n=20)[18], 2),  # 95th percentile
            'success_rate': round(len(response_times) / requests_count * 100, 1)
        }
    return None

def main():
    # Test key endpoints under load
    base_url = 'http://149.154.65.180:8002'
    endpoints = [
        '/api/health',
        '/api/phishing/sensitivity',
        '/api/analytics/overview',
        '/api/system/health'
    ]

    print('🔥 ALADDIN PERFORMANCE LOAD TESTING')
    print('=' * 60)

    all_results = []
    for endpoint in endpoints:
        url = f'{base_url}{endpoint}'
        print(f'\nTesting {endpoint}...')
        result = load_test_endpoint(url, 50)
        if result:
            all_results.append(result)
            print(f'  ✅ {result["total_requests"]}/50 successful')
            print(f'  ⏱️  Avg: {result["avg_time"]}ms | P95: {result["p95_time"]}ms | Min: {result["min_time"]}ms | Max: {result["max_time"]}ms')

    print('\n' + '=' * 60)
    print('📊 PERFORMANCE SUMMARY')

    if all_results:
        avg_response_times = [r['avg_time'] for r in all_results]
        p95_times = [r['p95_time'] for r in all_results]
        success_rates = [r['success_rate'] for r in all_results]

        print(f'Overall average response time: {round(statistics.mean(avg_response_times), 2)}ms')
        print(f'Overall P95 response time: {round(statistics.mean(p95_times), 2)}ms')
        print(f'Overall success rate: {round(statistics.mean(success_rates), 1)}%')

        # Performance criteria
        if statistics.mean(avg_response_times) < 200 and statistics.mean(success_rates) > 95:
            print('✅ PERFORMANCE: EXCELLENT - Ready for production')
            return True
        elif statistics.mean(avg_response_times) < 500 and statistics.mean(success_rates) > 90:
            print('✅ PERFORMANCE: GOOD - Acceptable for production')
            return True
        else:
            print('⚠️ PERFORMANCE: NEEDS IMPROVEMENT')
            return False
    else:
        print('❌ No performance data collected')
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)