#!/usr/bin/env python3
"""
🧪 COMPLETE API TESTING SCRIPT FOR 183 DECORATORS
Тестирование всех 183 декораторов в api_gateway_complete.py
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys

class API183Tester:
    def __init__(self, base_url: str = "http://149.154.65.180:8002"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0

    def extract_endpoints_from_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract all endpoints from api_gateway_complete.py"""
        endpoints = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_method = None
            current_path = None

            for line in lines:
                line = line.strip()

                # Find HTTP method decorators
                if line.startswith('@app.'):
                    import re

                    if 'get(' in line:
                        current_method = 'GET'
                        match = re.search(r'@app\.get\((.*?)\)', line)
                        if match:
                            path_str = match.group(1).strip()
                            current_path = path_str.strip('"\'')  # Remove quotes

                    elif 'post(' in line:
                        current_method = 'POST'
                        match = re.search(r'@app\.post\((.*?)\)', line)
                        if match:
                            path_str = match.group(1).strip()
                            current_path = path_str.strip('"\'')  # Remove quotes

                    elif 'put(' in line:
                        current_method = 'PUT'
                        match = re.search(r'@app\.put\((.*?)\)', line)
                        if match:
                            path_str = match.group(1).strip()
                            current_path = path_str.strip('"\'')  # Remove quotes

                    elif 'delete(' in line:
                        current_method = 'DELETE'
                        match = re.search(r'@app\.delete\((.*?)\)', line)
                        if match:
                            path_str = match.group(1).strip()
                            current_path = path_str.strip('"\'')  # Remove quotes

                # Find function definition to complete endpoint (support both sync and async)
                elif current_method and current_path and (line.startswith('def ') or line.startswith('async def ')):
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    endpoints.append((current_method, current_path, func_name))
                    current_method = None
                    current_path = None

        except Exception as e:
            print(f"❌ Error parsing file: {e}")

        return endpoints

    def test_endpoint(self, method: str, path: str, func_name: str) -> Dict:
        """Test single endpoint"""
        url = f"{self.base_url}{path}"
        start_time = time.time()

        try:
            # Prepare request based on method
            if method == 'GET':
                response = self.session.get(url, timeout=30)
            elif method == 'POST':
                # Use minimal test data for POST requests
                test_data = self.get_test_data_for_endpoint(path)
                response = self.session.post(url, json=test_data, timeout=30)
            elif method == 'PUT':
                test_data = self.get_test_data_for_endpoint(path)
                response = self.session.put(url, json=test_data, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                return {
                    'method': method,
                    'path': path,
                    'function': func_name,
                    'status': 'ERROR',
                    'response_time': 0,
                    'error': f'Unsupported method: {method}'
                }

            response_time = int((time.time() - start_time) * 1000)  # ms

            # Check for SFM integration
            sfm_integration = False
            try:
                response_data = response.json()
                if isinstance(response_data, dict) and 'source' in response_data:
                    if response_data.get('source') == 'real_sfm':
                        sfm_integration = True
            except:
                pass

            result = {
                'method': method,
                'path': path,
                'function': func_name,
                'status': 'SUCCESS' if response.status_code < 500 else 'ERROR',
                'http_status': response.status_code,
                'response_time': response_time,
                'sfm_integration': sfm_integration,
                'error': None if response.status_code < 500 else f'HTTP {response.status_code}'
            }

            if result['status'] == 'SUCCESS':
                self.passed_tests += 1

        except requests.exceptions.RequestException as e:
            result = {
                'method': method,
                'path': path,
                'function': func_name,
                'status': 'ERROR',
                'response_time': int((time.time() - start_time) * 1000),
                'sfm_integration': False,
                'error': str(e)
            }

        self.total_tests += 1
        return result

    def get_test_data_for_endpoint(self, path: str) -> Dict:
        """Generate test data based on endpoint path"""
        test_data = {}

        # Authentication endpoints
        if '/auth/register' in path:
            test_data = {
                "username": "test_user",
                "email": "test@example.com",
                "password": "test_password",
                "device_info": {"platform": "ios", "version": "15.0"}
            }
        elif '/auth/login' in path:
            test_data = {
                "username": "test_user",
                "password": "test_password",
                "device_fingerprint": "test_device_id"
            }
        elif '/auth/refresh' in path:
            test_data = {"refresh_token": "test_refresh_token"}

        # Subscription endpoints
        elif '/subscription/upgrade' in path:
            test_data = {"new_plan": "premium", "payment_method": "card"}

        # Notification endpoints
        elif '/notifications/mark_read' in path:
            test_data = {"notification_ids": ["test_id"]}

        # Parental control
        elif '/parental/restrict' in path:
            test_data = {
                "restriction_type": "website_block",
                "target": "social_media",
                "duration": 3600
            }

        # Anti-tracker
        elif '/antitracker/scan' in path:
            test_data = {
                "scan_type": "quick_scan",
                "target": "example.com",
                "deep_analysis": False
            }

        # Default minimal data
        return test_data

    def run_full_test(self, file_path: str) -> Dict:
        """Run complete test suite for all 183 endpoints"""
        print("🚀 STARTING COMPLETE API TEST SUITE (183 DECORATORS)")
        print("=" * 60)

        # Extract endpoints
        endpoints = self.extract_endpoints_from_file(file_path)
        print(f"📊 Found {len(endpoints)} endpoints to test")

        if len(endpoints) != 183:
            print(f"⚠️ Warning: Expected 183 endpoints, found {len(endpoints)}")

        # Test each endpoint
        for i, (method, path, func_name) in enumerate(endpoints, 1):
            print(f"🧪 Testing {i}/183: {method} {path}")
            result = self.test_endpoint(method, path, func_name)
            self.results.append(result)

            # Progress indicator
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            sfm_icon = "🔐" if result['sfm_integration'] else "⚠️"
            print(f"   {status_icon} {sfm_icon} {result['response_time']}ms")

        # Generate summary
        return self.generate_summary()

    def generate_summary(self) -> Dict:
        """Generate comprehensive test summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': self.total_tests,
            'successful_tests': self.passed_tests,
            'failed_tests': self.total_tests - self.passed_tests,
            'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
            'sfm_integration_count': sum(1 for r in self.results if r.get('sfm_integration')),
            'avg_response_time': sum(r['response_time'] for r in self.results) / len(self.results) if self.results else 0,
            'performance_stats': self.analyze_performance(),
            'results': self.results
        }

        return summary

    def analyze_performance(self) -> Dict:
        """Analyze performance metrics"""
        if not self.results:
            return {}

        response_times = [r['response_time'] for r in self.results]
        response_times.sort()

        return {
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p50_response_time': response_times[len(response_times) // 2],
            'p95_response_time': response_times[int(len(response_times) * 0.95)],
            'p99_response_time': response_times[int(len(response_times) * 0.99)] if len(response_times) > 100 else max(response_times),
            'under_200ms': sum(1 for t in response_times if t < 200),
            'over_1000ms': sum(1 for t in response_times if t > 1000)
        }

    def save_results(self, summary: Dict, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_183_test_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_complete_api_183_endpoints.py <api_gateway_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    tester = API183Tester()
    summary = tester.run_full_test(file_path)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY (183 DECORATORS)")
    print("=" * 60)
    print(f"✅ Successful: {summary['successful_tests']}/{summary['total_endpoints']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(".1f")
    print(f"🔐 SFM Integration: {summary['sfm_integration_count']}/183")
    print(".1f")
    print(f"📈 Performance (95-й перцентиль): {summary['performance_stats'].get('p95_response_time', 0)}ms")

    # Save results
    tester.save_results(summary)

    # Exit with appropriate code
    if summary['success_rate'] >= 95:
        print("🎉 TEST PASSED! Ready for production deployment.")
        sys.exit(0)
    else:
        print("❌ TEST FAILED! Check results before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()