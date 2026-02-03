#!/usr/bin/env python3
"""
COMPLETE ENDPOINT TESTING FOR ALADDIN PRODUCTION
Тестирование всех 108 API эндпоинтов на предмет реальных данных защиты
"""

import requests
import json
import time
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class EndpointTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'total_endpoints': 0,
            'tested_endpoints': 0,
            'real_data_endpoints': 0,
            'mock_data_endpoints': 0,
            'failed_endpoints': 0,
            'errors': [],
            'response_times': [],
            'endpoint_results': []
        }

    def get_all_endpoints(self) -> List[str]:
        """Get list of all API endpoints to test"""
        # Extract endpoints from API Gateway code
        endpoints = []

        try:
            with open('api_gateway_current.py', 'r') as f:
                content = f.read()

            import re
            # Find all @app.get, @app.post, @app.put, @app.delete decorators
            pattern = r'@app\.(get|post|put|delete)\("([^"]+)"\)'
            matches = re.findall(pattern, content)

            for method, path in matches:
                if path.startswith('/api/'):
                    endpoints.append(path)

        except Exception as e:
            print(f"Error reading endpoints: {e}")
            # Fallback list of known endpoints
            endpoints = [
                "/api/health",
                "/api/phishing/sensitivity",
                "/api/phishing/block_suspicious",
                "/api/phishing/exclusions",
                "/api/malware/scan_scheduled",
                "/api/malware/quarantine",
                "/api/malware/scan_now",
                "/api/mobile/app_lock",
                "/api/mobile/biometric",
                "/api/network/firewall_rules",
                "/api/network/vpn_config",
                "/api/monitoring/ai_categories_stats",
                "/api/monitoring/ai_categories_reports",
                "/api/monitoring/data_cleanup_stats",
                "/api/monitoring/data_cleanup_records",
                "/api/monitoring/location_stats",
                "/api/monitoring/location_requests",
                "/api/monitoring/darkweb_leaks",
                "/api/monitoring/darkweb_stats",
                "/api/monitoring/darkweb_scans",
                "/api/monitoring/identity_attempts",
                "/api/monitoring/identity_stats",
                "/api/protection/identity_theft_attempts",
                "/api/protection/identity_theft_stats",
                "/api/protection/antitracker_trackers",
                "/api/protection/antitracker_stats",
                "/api/protection/antitracker_categories",
                "/api/protection/parental_stats",
                "/api/protection/parental_activity",
                "/api/protection/roadside_history",
                "/api/notifications/list",
                "/api/notifications/stats",
                "/api/notifications/unread_count",
                "/api/analytics/overview",
                "/api/analytics/security_events",
                "/api/analytics/performance",
                "/api/analytics/reports",
                "/api/subscription/status",
                "/api/subscription/plans",
                "/api/subscription/billing_history",
                "/api/user/profile",
                "/api/system/info",
                "/api/system/health",
                "/api/system/logs"
            ]

        return list(set(endpoints))  # Remove duplicates

    def test_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test single endpoint"""
        start_time = time.time()

        try:
            url = f"{self.base_url}{endpoint}"

            # Choose HTTP method based on endpoint
            if any(keyword in endpoint for keyword in ['enable', 'disable', 'update', 'create', 'send', 'test', 'mark']):
                method = 'POST' if 'POST' in endpoint.upper() else 'PUT'
            else:
                method = 'GET'

            # Add test parameters for endpoints that need them
            params = {}
            if 'limit' in endpoint:
                params['limit'] = 10
            if 'period' in endpoint:
                params['period'] = 'month'

            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            else:
                # For POST/PUT, send empty JSON if no specific data needed
                response = self.session.post(url, json={}, timeout=10)

            response_time = time.time() - start_time

            # Analyze response
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'response_time': round(response_time * 1000, 2),  # ms
                'success': response.status_code == 200,
                'has_real_data': False,
                'data_type': 'unknown',
                'error': None
            }

            if response.status_code == 200:
                try:
                    data = response.json()

                    # Check if response contains real protection data
                    if isinstance(data, dict):
                        source = data.get('source', '')
                        if 'sfm_real' in source or 'protection' in source:
                            result['has_real_data'] = True
                            result['data_type'] = 'real_protection'
                        elif 'mock' in source:
                            result['has_real_data'] = False
                            result['data_type'] = 'mock'
                        else:
                            # Check for protection-related fields
                            protection_fields = [
                                'blocked_phishing_attempts', 'threats_blocked', 'active_rules_count',
                                'detection_accuracy', 'protection_status', 'ml_model_version'
                            ]
                            if any(field in data for field in protection_fields):
                                result['has_real_data'] = True
                                result['data_type'] = 'real_protection'
                            else:
                                result['data_type'] = 'other'

                    result['data_keys'] = list(data.keys()) if isinstance(data, dict) else 'not_dict'

                except json.JSONDecodeError:
                    result['error'] = 'Invalid JSON response'
                    result['success'] = False
            else:
                result['error'] = f'HTTP {response.status_code}'
                result['success'] = False

        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'endpoint': endpoint,
                'method': method if 'method' in locals() else 'GET',
                'status_code': None,
                'response_time': round(response_time * 1000, 2),
                'success': False,
                'has_real_data': False,
                'data_type': 'error',
                'error': str(e)
            }

        return result

    def run_full_test(self, max_workers: int = 10) -> Dict[str, Any]:
        """Run complete endpoint testing"""
        print("🚀 STARTING COMPLETE ENDPOINT TESTING...")

        endpoints = self.get_all_endpoints()
        self.results['total_endpoints'] = len(endpoints)

        print(f"📊 Found {len(endpoints)} endpoints to test")

        # Test endpoints concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_endpoint = {
                executor.submit(self.test_endpoint, endpoint): endpoint
                for endpoint in endpoints
            }

            for future in as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    result = future.result()
                    self.results['tested_endpoints'] += 1
                    self.results['endpoint_results'].append(result)

                    # Update counters
                    if result['success']:
                        if result['has_real_data']:
                            self.results['real_data_endpoints'] += 1
                        else:
                            self.results['mock_data_endpoints'] += 1
                    else:
                        self.results['failed_endpoints'] += 1
                        self.results['errors'].append(result)

                    self.results['response_times'].append(result['response_time'])

                    # Progress indicator
                    progress = self.results['tested_endpoints'] / self.results['total_endpoints'] * 100
                    status = "✅" if result['success'] and result['has_real_data'] else "⚠️" if result['success'] else "❌"
                    print(f"{status} [{progress:.1f}%] {result['endpoint']} - {result['data_type']} ({result['response_time']}ms)")

                except Exception as e:
                    print(f"❌ Error testing {endpoint}: {e}")
                    self.results['failed_endpoints'] += 1

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if self.results['response_times']:
            avg_response_time = sum(self.results['response_times']) / len(self.results['response_times'])
            min_response_time = min(self.results['response_times'])
            max_response_time = max(self.results['response_times'])
        else:
            avg_response_time = min_response_time = max_response_time = 0

        report = {
            **self.results,
            'summary': {
                'total_tested': self.results['tested_endpoints'],
                'success_rate': (self.results['tested_endpoints'] - self.results['failed_endpoints']) / max(self.results['tested_endpoints'], 1) * 100,
                'real_data_rate': self.results['real_data_endpoints'] / max(self.results['tested_endpoints'], 1) * 100,
                'avg_response_time_ms': round(avg_response_time, 2),
                'min_response_time_ms': round(min_response_time, 2),
                'max_response_time_ms': round(max_response_time, 2)
            },
            'production_ready': self.is_production_ready(),
            'recommendations': self.get_recommendations()
        }

        return report

    def is_production_ready(self) -> bool:
        """Check if system is ready for production"""
        success_rate = (self.results['tested_endpoints'] - self.results['failed_endpoints']) / max(self.results['tested_endpoints'], 1)
        real_data_rate = self.results['real_data_endpoints'] / max(self.results['tested_endpoints'], 1)
        avg_response_time = sum(self.results['response_times']) / max(len(self.results['response_times']), 1)

        return (
            success_rate >= 0.95 and  # 95% success rate
            real_data_rate >= 0.80 and  # 80% real data
            avg_response_time < 1000  # < 1 second average response
        )

    def get_recommendations(self) -> List[str]:
        """Get production recommendations"""
        recommendations = []

        success_rate = (self.results['tested_endpoints'] - self.results['failed_endpoints']) / max(self.results['tested_endpoints'], 1)
        real_data_rate = self.results['real_data_endpoints'] / max(self.results['tested_endpoints'], 1)

        if success_rate < 0.95:
            recommendations.append("Fix failing endpoints before production")

        if real_data_rate < 0.80:
            recommendations.append("Replace remaining mock data with real protection data")

        if self.results['failed_endpoints'] > 0:
            recommendations.append(f"Address {self.results['failed_endpoints']} failed endpoints")

        if not recommendations:
            recommendations.append("System ready for production launch!")

        return recommendations

def main():
    """Main testing function"""
    print("=" * 70)
    print("🛡️ ALADDIN COMPLETE ENDPOINT TESTING")
    print("=" * 70)

    tester = EndpointTester()

    # Run full test
    report = tester.run_full_test()

    print("\n" + "=" * 70)
    print("📊 FINAL TEST REPORT")
    print("=" * 70)

    print(f"Total endpoints: {report['total_endpoints']}")
    print(f"Tested endpoints: {report['tested_endpoints']}")
    print(f"Successful endpoints: {report['tested_endpoints'] - report['failed_endpoints']}")
    print(f"Failed endpoints: {report['failed_endpoints']}")
    print(f"Real data endpoints: {report['real_data_endpoints']}")
    print(f"Mock data endpoints: {report['mock_data_endpoints']}")

    print("\n⏱️ Performance:"    print(".2f")
    print(".2f")
    print(".2f")
    print("\n📈 Success Rates:")
    print(".1f")
    print(".1f")
    print("\n🎯 Production Status:")
    status = "✅ READY" if report['production_ready'] else "⚠️ NEEDS WORK"
    print(f"Status: {status}")

    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")

    if report['failed_endpoints'] > 0:
        print("\n❌ Failed endpoints:")
        for error in report['errors'][:5]:  # Show first 5
            print(f"  • {error['endpoint']}: {error['error']}")

    print("\n" + "=" * 70)

    # Save detailed report
    with open('endpoint_test_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print("📄 Detailed report saved: endpoint_test_report.json")

    return report['production_ready']

if __name__ == "__main__":
    import sys
    ready = main()
    sys.exit(0 if ready else 1)