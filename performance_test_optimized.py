#!/usr/bin/env python3
"""
🧪 OPTIMIZED API Performance Test
Проверка производительности после оптимизаций
"""

import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "https://149.154.65.180/api"
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

BATCH_ENDPOINT = "/components/status/batch"
REQUESTS_PER_ENDPOINT = 20
CONCURRENT_REQUESTS = 10
TIMEOUT = 30

class OptimizedAPIPerformanceTester:
    def __init__(self, base_url, endpoints, batch_endpoint, requests_per_endpoint=20):
        self.base_url = base_url
        self.endpoints = endpoints
        self.batch_endpoint = batch_endpoint
        self.requests_per_endpoint = requests_per_endpoint
        self.session = requests.Session()

        # Configure optimized session
        self.session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json',
            'User-Agent': 'ALADDIN-iOS/1.0.0'
        })

        # Disable SSL verification for testing
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

    def test_batch_performance(self):
        """Test batch endpoint performance"""
        print("🚀 Testing batch endpoint performance...")

        # Test batch request with all component IDs
        component_ids = [
            "crash_detection_agent", "emergency_response_bot", "emergency_event_manager",
            "phishing_protection_agent", "malware_detection_agent", "password_security_agent",
            "mobile_security_agent", "network_security_agent", "incident_response_agent",
            "roadside_assistance_agent"
        ]

        batch_times = []

        for i in range(self.requests_per_endpoint):
            start_time = time.time()

            try:
                batch_data = {"component_ids": component_ids}
                response = self.session.post(
                    f"{self.base_url}{self.batch_endpoint}",
                    json=batch_data,
                    timeout=TIMEOUT
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    batch_times.append(response_time)
                else:
                    print(f"   ⚠️ Batch request {i} failed with status {response.status_code}")

            except Exception as e:
                print(f"   ❌ Batch request {i} error: {e}")

        if batch_times:
            batch_p95 = sorted(batch_times)[int(len(batch_times) * 0.95)]
            batch_avg = sum(batch_times) / len(batch_times)

            print("   📊 Batch Performance Results:")
            print(f"   - Requests: {len(batch_times)}/{self.requests_per_endpoint}")
            print(f"   - P95: {p95:.3f}s")
            print(f"   - Avg: {avg:.3f}s")
            return {
                'batch_p95': batch_p95,
                'batch_avg': batch_avg,
                'batch_requests': len(batch_times),
                'individual_equivalent': len(component_ids) * len(batch_times)  # How many individual requests this replaces
            }
        else:
            return {'error': 'No successful batch requests'}

    def test_individual_performance(self):
        """Test individual endpoint performance"""
        print("📊 Testing individual endpoint performance...")

        results = {}

        for endpoint in self.endpoints:
            print(f"   Testing {endpoint}...")
            response_times = []

            for i in range(self.requests_per_endpoint):
                response_time, success, status_code = self.make_request(endpoint)
                if success:
                    response_times.append(response_time)

            if response_times:
                sorted_times = sorted(response_times)
                p95 = sorted_times[int(len(response_times) * 0.95)]
                avg = sum(response_times) / len(response_times)

                results[endpoint] = {
                    'p95': p95,
                    'avg': avg,
                    'requests': len(response_times)
                }

                print(f"   - P95: {p95:.3f}s")
            else:
                print(f"     ❌ No successful requests")

        return results

    def compare_batch_vs_individual(self, batch_results, individual_results):
        """Compare batch vs individual performance"""
        print("\n🔍 Comparing Batch vs Individual Performance")

        if 'error' in batch_results:
            print("❌ Cannot compare - batch requests failed")
            return

        # Calculate total individual time for all endpoints
        total_individual_p95 = 0
        total_requests = 0

        for endpoint, result in individual_results.items():
            if 'p95' in result:
                total_individual_p95 += result['p95']
                total_requests += result['requests']

        avg_individual_p95 = total_individual_p95 / len(individual_results) if individual_results else 0

        batch_p95 = batch_results['batch_p95']
        batch_equivalent = batch_results['individual_equivalent']

        improvement = ((avg_individual_p95 - batch_p95) / avg_individual_p95) * 100 if avg_individual_p95 > 0 else 0

        print("   📈 Performance Comparison:")
        print(f"   - Individual Avg P95: {avg_individual_p95:.3f}s")
        print(f"   - Batch P95: {batch_p95:.3f}s")
        print(f"   - Improvement: {improvement:.1f}%")
        print(f"   - Batch replaces {batch_equivalent} individual requests")

        return {
            'individual_avg_p95': avg_individual_p95,
            'batch_p95': batch_p95,
            'improvement_percent': improvement,
            'efficiency_ratio': batch_equivalent / batch_results['batch_requests'] if batch_results['batch_requests'] > 0 else 0
        }

    def test_connection_optimization(self):
        """Test connection optimization effects"""
        print("🔗 Testing connection optimization...")

        # Test multiple sequential requests to same endpoint (should reuse connections)
        endpoint = self.endpoints[0]
        sequential_times = []

        print(f"   Making {self.requests_per_endpoint} sequential requests to {endpoint}...")

        for i in range(self.requests_per_endpoint):
            response_time, success, status_code = self.make_request(endpoint)
            if success:
                sequential_times.append(response_time)

        if sequential_times:
            # Check if later requests are faster (connection reuse)
            first_half = sequential_times[:len(sequential_times)//2]
            second_half = sequential_times[len(sequential_times)//2:]

            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            connection_reuse_improvement = ((first_avg - second_avg) / first_avg) * 100

            print("   🔄 Connection Reuse Analysis:")
            print(f"   - P95: {p95:.3f}s")
            print(f"   - Avg: {avg:.3f}s")
            print(f"   - Connection reuse improvement: {connection_reuse_improvement:.1f}%")
            return {
                'first_half_avg': first_avg,
                'second_half_avg': second_avg,
                'connection_reuse_improvement': connection_reuse_improvement,
                'total_requests': len(sequential_times)
            }

        return {'error': 'No successful sequential requests'}

    def run_complete_test(self):
        """Run complete optimized performance test suite"""
        print("🚀 ALADDIN OPTIMIZED API Performance Test")
        print("=" * 60)

        start_time = time.time()

        # Test batch performance
        batch_results = self.test_batch_performance()
        print()

        # Test individual performance
        individual_results = self.test_individual_performance()
        print()

        # Compare batch vs individual
        comparison_results = self.compare_batch_vs_individual(batch_results, individual_results)
        print()

        # Test connection optimization
        connection_results = self.test_connection_optimization()

        test_duration = time.time() - start_time

        print(f"\n⏱️ Complete test duration: {test_duration:.1f} seconds")

        # Overall results
        print("\n📊 OPTIMIZATION RESULTS")
        print("=" * 60)

        # Calculate overall metrics
        all_individual_times = []
        for endpoint, result in individual_results.items():
            if 'p95' in result:
                all_individual_times.append(result['p95'])

        if all_individual_times:
            overall_individual_p95 = sum(all_individual_times) / len(all_individual_times)

            if 'error' not in batch_results:
                batch_p95 = batch_results['batch_p95']
                optimization_factor = overall_individual_p95 / batch_p95 if batch_p95 > 0 else 0

                print("🎯 OPTIMIZATION ACHIEVEMENTS:")
                print(f"   - Individual P95: {overall_individual_p95:.3f}s")
                print(f"   - Batch P95: {batch_p95:.3f}s")
                print(f"   - Optimization Factor: {optimization_factor:.1f}x")
                print(f"   - SLA Target: {0.025:.3f}s (25ms)")
                # SLA Check
                sla_passed = batch_p95 < 0.025  # 25ms target
                if sla_passed:
                    print("🎉 SLA ACHIEVED: Batch P95 < 25ms ✅")
                else:
                    remaining_ms = (batch_p95 - 0.025) * 1000
                    print(f"   - Remaining to SLA: {remaining_ms:.1f}ms")
            else:
                print("❌ Batch requests failed - cannot achieve SLA")

            return {
                'batch_results': batch_results,
                'individual_results': individual_results,
                'comparison_results': comparison_results,
                'connection_results': connection_results,
                'test_duration': test_duration,
                'optimization_achieved': sla_passed if 'batch_results' in locals() and 'error' not in batch_results else False
            }
        else:
            print("❌ No individual request data available")
            return {'error': 'No performance data'}

def main():
    tester = OptimizedAPIPerformanceTester(BASE_URL, ENDPOINTS, BATCH_ENDPOINT, REQUESTS_PER_ENDPOINT)

    results = tester.run_complete_test()

    # Save detailed results
    with open('optimized_performance_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n💾 Detailed results saved to optimized_performance_results.json")
    # Save summary
    summary = {
        'test_timestamp': str(__import__('datetime').datetime.now()),
        'optimization_status': 'PASSED' if results.get('optimization_achieved', False) else 'FAILED',
        'key_metrics': {
            'batch_p95': results.get('batch_results', {}).get('batch_p95', 'N/A'),
            'individual_avg_p95': results.get('comparison_results', {}).get('individual_avg_p95', 'N/A'),
            'improvement_percent': results.get('comparison_results', {}).get('improvement_percent', 'N/A'),
            'connection_reuse_improvement': results.get('connection_results', {}).get('connection_reuse_improvement', 'N/A')
        }
    }

    with open('optimization_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("💾 Summary saved to optimization_summary.json")

if __name__ == "__main__":
    main()