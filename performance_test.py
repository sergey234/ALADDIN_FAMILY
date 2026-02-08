#!/usr/bin/env python3
"""
🧪 ALADDIN iOS API Performance Test
Измерение 95-го перцентиля API response times
Цель: <25ms для 95-го перцентиля
"""

import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "https://aladdin-ai.ru/api"
ENDPOINTS = [
    "/health",
    "/components/status/crash_detection_agent",
    "/components/status/phishing_protection_agent",
    "/components/status/mobile_security_agent",
    "/components/status/network_security_agent",
    "/components/status/emergency_response_bot",
    "/components/status/emergency_event_manager",
    "/components/status/incident_response_agent",
    "/components/status/password_security_agent",
    "/components/status/malware_detection_agent"
]

REQUESTS_PER_ENDPOINT = 50
CONCURRENT_REQUESTS = 10
TIMEOUT = 30

class APIPerformanceTester:
    def __init__(self, base_url, endpoints, requests_per_endpoint=50):
        self.base_url = base_url
        self.endpoints = endpoints
        self.requests_per_endpoint = requests_per_endpoint
        self.session = requests.Session()

        # Disable SSL verification for testing (use real certificates in production)
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def make_request(self, endpoint):
        """Make a single API request and return response time"""
        start_time = time.time()
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, timeout=TIMEOUT)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return response_time, True, response.status_code
            else:
                return response_time, False, response.status_code

        except Exception as e:
            response_time = time.time() - start_time
            return response_time, False, 0

    def test_endpoint_performance(self, endpoint):
        """Test performance for a single endpoint"""
        print(f"📊 Testing {endpoint}...")

        response_times = []
        success_count = 0

        # Sequential requests for accurate timing
        for i in range(self.requests_per_endpoint):
            response_time, success, status_code = self.make_request(endpoint)

            if success:
                response_times.append(response_time)
                success_count += 1

        if response_times:
            sorted_times = sorted(response_times)
            p50 = statistics.median(sorted_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 100 else max(sorted_times)

            return {
                'endpoint': endpoint,
                'total_requests': self.requests_per_endpoint,
                'successful_requests': success_count,
                'success_rate': success_count / self.requests_per_endpoint,
                'response_times': response_times,
                'p50': p50,
                'p95': p95,
                'p99': p99,
                'min': min(sorted_times),
                'max': max(sorted_times),
                'avg': sum(response_times) / len(response_times)
            }
        else:
            return {
                'endpoint': endpoint,
                'total_requests': self.requests_per_endpoint,
                'successful_requests': 0,
                'success_rate': 0,
                'error': 'No successful requests'
            }

    def test_concurrent_load(self):
        """Test API performance under concurrent load"""
        print("🔄 Testing concurrent load...")

        response_times = []

        def worker():
            results = []
            for endpoint in self.endpoints:
                response_time, success, status_code = self.make_request(endpoint)
                if success:
                    results.append(response_time)
            return results

        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = [executor.submit(worker) for _ in range(20)]  # 20 concurrent workers

            for future in as_completed(futures):
                try:
                    results = future.result()
                    response_times.extend(results)
                except Exception as e:
                    print(f"❌ Worker failed: {e}")

        if response_times:
            sorted_times = sorted(response_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]

            return {
                'concurrent_requests': CONCURRENT_REQUESTS * 20,  # workers * endpoints_per_worker
                'total_responses': len(response_times),
                'p95_concurrent': p95,
                'avg_concurrent': sum(response_times) / len(response_times)
            }
        else:
            return {'error': 'No responses under concurrent load'}

    def run_full_test(self):
        """Run complete performance test suite"""
        print("🚀 Starting ALADDIN API Performance Test")
        print("=" * 60)

        # Test individual endpoints
        results = []
        for endpoint in self.endpoints:
            result = self.test_endpoint_performance(endpoint)
            results.append(result)

            if 'error' not in result:
                print(f"   Success rate: {result['success_rate']:.1%}")
                print(f"   P95: {result['p95']:.3f}s")
            else:
                print(f"❌ Failed: {result['error']}")
            print("-" * 40)

        # Test concurrent load
        concurrent_result = self.test_concurrent_load()
        if 'error' not in concurrent_result:
            print("🔄 Concurrent Load Results:")
            print(f"   Requests: {concurrent_result['concurrent_requests']}")
            print(f"   Responses: {concurrent_result['total_responses']}")
            print(f"   P95: {concurrent_result['p95_concurrent']:.3f}s")
            print(f"   Avg: {concurrent_result['avg_concurrent']:.3f}s")
        else:
            print(f"❌ Concurrent test failed: {concurrent_result['error']}")

        # Overall results
        print("\n📊 OVERALL RESULTS")
        print("=" * 60)

        all_response_times = []
        successful_endpoints = 0

        for result in results:
            if 'error' not in result:
                successful_endpoints += 1
                all_response_times.extend(result['response_times'])

        if all_response_times:
            overall_p95 = sorted(all_response_times)[int(len(all_response_times) * 0.95)]
            overall_avg = sum(all_response_times) / len(all_response_times)

            print(f"   Overall P95: {overall_p95:.3f}s")
            print(f"   Overall Avg: {overall_avg:.3f}s")
            print(f"✅ Endpoints tested: {successful_endpoints}/{len(self.endpoints)}")
            print(f"✅ Total requests: {len(all_response_times)}")

            # SLA Check
            sla_passed = overall_p95 < 0.025  # 25ms
            if sla_passed:
                print("🎉 SLA PASSED: 95th percentile < 25ms")
            else:
                print("❌ SLA FAILED: 95th percentile >= 25ms")

            return {
                'overall_p95': overall_p95,
                'overall_avg': overall_avg,
                'sla_passed': sla_passed,
                'endpoints_tested': successful_endpoints,
                'total_requests': len(all_response_times),
                'endpoint_results': results,
                'concurrent_results': concurrent_result
            }
        else:
            print("❌ No successful requests - API may be down")
            return {'error': 'No successful requests'}

def main():
    tester = APIPerformanceTester(BASE_URL, ENDPOINTS, REQUESTS_PER_ENDPOINT)

    start_time = time.time()
    results = tester.run_full_test()
    test_duration = time.time() - start_time

    print(f"\n⏱️ Test completed in {test_duration:.1f} seconds")

    # Save results
    with open('performance_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("💾 Results saved to performance_test_results.json")

if __name__ == "__main__":
    main()