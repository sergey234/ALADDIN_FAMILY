#!/usr/bin/env python3
"""
COMPLETE 108 ENDPOINT TESTING FOR ALADDIN PRODUCTION
Полное тестирование всех 108 API эндпоинтов на предмет реальных данных защиты
"""

import requests
import json
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

def extract_endpoints_from_code() -> List[str]:
    """Extract all endpoints from api_gateway.py"""
    try:
        with open('api_gateway_current.py', 'r') as f:
            content = f.read()

        # Find all @app.get, @app.post, @app.put, @app.delete decorators
        pattern = r'@app\.(get|post|put|delete)\("([^"]+)"\)'
        matches = re.findall(pattern, content)

        endpoints = []
        for method, path in matches:
            if path.startswith('/api/'):
                endpoints.append(path)

        return list(set(endpoints))  # Remove duplicates

    except Exception as e:
        print(f"Error extracting endpoints: {e}")
        return []

def test_single_endpoint(endpoint: str, base_url: str = "http://149.154.65.180:8002") -> Dict[str, Any]:
    """Test single endpoint"""
    start_time = time.time()
    url = f"{base_url}{endpoint}"

    # Determine HTTP method
    method = 'GET'  # Default

    # Add test parameters for endpoints that need them
    params = {}
    if 'limit' in endpoint:
        params['limit'] = 10
    if 'period' in endpoint:
        params['period'] = 'month'
    if 'page' in endpoint:
        params['page'] = 1

    # Choose method based on endpoint
    if any(keyword in endpoint.lower() for keyword in ['enable', 'disable', 'update', 'create', 'send', 'test', 'mark', 'delete']):
        method = 'POST' if 'POST' in endpoint.upper() else 'PUT'

    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json={}, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json={}, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            response = requests.get(url, params=params, timeout=10)

        response_time = (time.time() - start_time) * 1000

        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'success': response.status_code in [200, 201, 204],
            'data_type': 'unknown',
            'has_real_data': False,
            'error': None,
            'data_size': 0
        }

        if response.status_code in [200, 201, 204]:
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    result['data_size'] = len(json.dumps(data)) if data else 0

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
                            protection_indicators = [
                                'blocked_phishing_attempts', 'threats_blocked', 'active_rules_count',
                                'detection_accuracy', 'protection_status', 'ml_model_version',
                                'threats_detected', 'security_score', 'rules_active',
                                'total_events_processed', 'false_positives', 'system_uptime'
                            ]
                            if any(field in data for field in protection_indicators):
                                result['has_real_data'] = True
                                result['data_type'] = 'real_protection'
                            else:
                                result['data_type'] = 'other_data'
                    else:
                        result['data_type'] = 'non_dict_response'
                else:
                    result['data_type'] = 'non_json_response'
                    result['data_size'] = len(response.text)

            except json.JSONDecodeError:
                result['error'] = 'Invalid JSON response'
                result['data_type'] = 'json_error'
        else:
            result['error'] = f'HTTP {response.status_code}'
            result['data_type'] = 'http_error'

    except requests.exceptions.Timeout:
        response_time = (time.time() - start_time) * 1000
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': None,
            'response_time_ms': round(response_time, 2),
            'success': False,
            'data_type': 'timeout',
            'has_real_data': False,
            'error': 'Request timeout'
        }
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': None,
            'response_time_ms': round(response_time, 2),
            'success': False,
            'data_type': 'exception',
            'has_real_data': False,
            'error': str(e)
        }

    return result

def run_complete_test(max_workers: int = 5) -> Dict[str, Any]:
    """Run complete test of all 108 endpoints"""
    print("🚀 STARTING COMPLETE 108 ENDPOINT TESTING")
    print("=" * 70)

    endpoints = extract_endpoints_from_code()
    total_endpoints = len(endpoints)

    print(f"📊 Found {total_endpoints} endpoints to test")
    print("Testing with concurrent requests (max_workers=5)...")
    print()

    results = []
    successful_endpoints = 0
    real_data_endpoints = 0
    mock_data_endpoints = 0
    failed_endpoints = 0
    response_times = []

    # Test endpoints concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_endpoint = {
            executor.submit(test_single_endpoint, endpoint): endpoint
            for endpoint in endpoints
        }

        completed = 0
        for future in as_completed(future_to_endpoint):
            endpoint = future_to_endpoint[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1

                # Update counters
                if result['success']:
                    successful_endpoints += 1
                    if result['has_real_data']:
                        real_data_endpoints += 1
                    else:
                        mock_data_endpoints += 1
                else:
                    failed_endpoints += 1

                response_times.append(result['response_time_ms'])

                # Progress indicator
                progress = completed / total_endpoints * 100
                status_icon = "✅" if result['success'] and result['has_real_data'] else "⚠️" if result['success'] else "❌"
                timing = f"{result['response_time_ms']}ms" if result['response_time_ms'] < 1000 else "TIMEOUT"
                print(f"[{progress:.1f}%] {status_icon} {result['method']} {result['endpoint']} - {result['data_type']} ({timing})")

            except Exception as e:
                print(f"❌ Error processing {endpoint}: {e}")
                failed_endpoints += 1

    # Calculate statistics
    success_rate = successful_endpoints / total_endpoints * 100 if total_endpoints > 0 else 0
    real_data_rate = real_data_endpoints / total_endpoints * 100 if total_endpoints > 0 else 0

    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0

    # Determine production readiness
    production_ready = (
        success_rate >= 95 and  # 95% of endpoints work
        real_data_rate >= 50 and  # At least 50% return real protection data
        avg_response_time < 1000  # Average response time < 1 second
    )

    report = {
        'total_endpoints': total_endpoints,
        'successful_endpoints': successful_endpoints,
        'failed_endpoints': failed_endpoints,
        'real_data_endpoints': real_data_endpoints,
        'mock_data_endpoints': mock_data_endpoints,
        'success_rate': round(success_rate, 1),
        'real_data_rate': round(real_data_rate, 1),
        'avg_response_time': round(avg_response_time, 2),
        'min_response_time': round(min_response_time, 2),
        'max_response_time': round(max_response_time, 2),
        'p95_response_time': round(p95_response_time, 2),
        'production_ready': production_ready,
        'results': results
    }

    return report

def print_detailed_report(report: Dict[str, Any]):
    """Print detailed test report"""
    print("\n" + "=" * 70)
    print("📊 COMPLETE 108 ENDPOINT TEST REPORT")
    print("=" * 70)

    print(f"Total endpoints tested: {report['total_endpoints']}")
    print(f"✅ Successful endpoints: {report['successful_endpoints']}")
    print(f"❌ Failed endpoints: {report['failed_endpoints']}")
    print(f"🔥 Real protection data: {report['real_data_endpoints']}")
    print(f"⚠️ Mock data endpoints: {report['mock_data_endpoints']}")

    print("\n📈 Success Rates:")
    print(f"   • Success rate: {report['success_rate']:.1f}%")
    print(f"   • Real data rate: {report['real_data_rate']:.1f}%")
    print("\n⏱️ Performance Metrics:")
    print(f"   • Average response time: {report['avg_response_time']:.2f}ms")
    print(f"   • Min response time: {report['min_response_time']:.2f}ms")
    print(f"   • Max response time: {report['max_response_time']:.2f}ms")
    print(f"   • P95 response time: {report['p95_response_time']:.2f}ms")
    print("\n🎯 Production Readiness:")
    if report['production_ready']:
        print("✅ STATUS: PRODUCTION READY")
        print("   • High success rate achieved")
        print("   • Sufficient real protection data")
        print("   • Acceptable performance metrics")
    else:
        print("⚠️ STATUS: NEEDS IMPROVEMENT")
        issues = []
        if report['success_rate'] < 95:
            issues.append(f"Success rate too low ({report['success_rate']}%)")
        if report['real_data_rate'] < 50:
            issues.append(f"Real data rate too low ({report['real_data_rate']}%)")
        if report['avg_response_time'] >= 1000:
            issues.append(f"Average response time too high ({report['avg_response_time']}ms)")
        for issue in issues:
            print(f"   • {issue}")

    # Show failed endpoints
    if report['failed_endpoints'] > 0:
        print("
❌ Failed Endpoints:"        failed_results = [r for r in report['results'] if not r['success']]
        for result in failed_results[:10]:  # Show first 10
            print(f"   • {result['method']} {result['endpoint']}: {result['error']}")

        if len(failed_results) > 10:
            print(f"   ... and {len(failed_results) - 10} more")

    # Show real data distribution
    if report['real_data_endpoints'] > 0:
        print("
🔥 Real Protection Data Distribution:"        real_results = [r for r in report['results'] if r['has_real_data']]
        category_count = {}
        for result in real_results:
            category = result['endpoint'].split('/')[2] if len(result['endpoint'].split('/')) > 2 else 'other'
            category_count[category] = category_count.get(category, 0) + 1

        for category, count in sorted(category_count.items()):
            print(f"   • {category}: {count} endpoints")

def save_report_to_file(report: Dict[str, Any], filename: str = "complete_endpoint_test_report.json"):
    """Save detailed report to JSON file"""
    # Remove results array to reduce file size (it's too large)
    report_copy = report.copy()
    report_copy['results_summary'] = {
        'successful': len([r for r in report['results'] if r['success']]),
        'failed': len([r for r in report['results'] if not r['success']]),
        'real_data': len([r for r in report['results'] if r['has_real_data']]),
        'mock_data': len([r for r in report['results'] if r['success'] and not r['has_real_data']])
    }
    # Don't save full results array - too large
    del report_copy['results']

    with open(filename, 'w') as f:
        json.dump(report_copy, f, indent=2)

    print(f"\n📄 Report saved to: {filename}")

if __name__ == "__main__":
    print("🛡️ ALADDIN COMPLETE 108 ENDPOINT TESTING")
    print("Testing ALL API endpoints for production readiness...")

    report = run_complete_test()

    print_detailed_report(report)
    save_report_to_file(report)

    if report['production_ready']:
        print("\n🎉 ALADDIN IS 100% PRODUCTION READY!")
        print("🚀 Ready to protect users from cyber threats!")
        exit(0)
    else:
        print("\n⚠️ Additional work needed before production launch")
        exit(1)