#!/usr/bin/env python3
"""
ALADDIN VPN - Security Systems Test Suite
Тестирование всех систем безопасности

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

# Импорт систем безопасности
from security_integration import check_security, get_security_dashboard, get_security_status
from protection.ddos_protection import DDoSProtectionSystem
from protection.rate_limiter import AdvancedRateLimiter
from protection.intrusion_detection import IntrusionDetectionSystem
from audit_logging.audit_logger import SecurityAuditLogger, log_audit_event, EventType
from auth.two_factor_auth import TwoFactorAuth, setup_user_2fa, verify_2fa_code, AuthMethod


class SecurityTestSuite:
    """Набор тестов для систем безопасности"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now(timezone.utc)
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🧪 ALADDIN VPN Security Systems Test Suite")
        print("=" * 60)
        
        # Тестируем каждую систему
        await self.test_ddos_protection()
        await self.test_rate_limiting()
        await self.test_intrusion_detection()
        await self.test_audit_logging()
        await self.test_two_factor_auth()
        await self.test_security_integration()
        
        # Генерируем отчет
        report = self.generate_report()
        self.save_report(report)
        
        return report
    
    async def test_ddos_protection(self):
        """Тестирование DDoS защиты"""
        print("\n🔒 Testing DDoS Protection System...")
        
        try:
            ddos = DDoSProtectionSystem()
            
            # Тест 1: Нормальные запросы
            normal_requests = [
                ("192.168.1.1", "/api/v1/status", "Mozilla/5.0"),
                ("192.168.1.2", "/vpn/servers", "Mozilla/5.0"),
                ("192.168.1.3", "/admin/dashboard", "Mozilla/5.0")
            ]
            
            normal_passed = 0
            for ip, endpoint, user_agent in normal_requests:
                allowed, message, action = await ddos.check_request(ip, endpoint, user_agent)
                if allowed:
                    normal_passed += 1
            
            # Тест 2: Подозрительные запросы
            suspicious_requests = [
                ("192.168.1.100", "/admin/backup", "sqlmap"),
                ("192.168.1.101", "/.env", "scanner"),
                ("192.168.1.102", "/api/v1/users", "bot")
            ]
            
            suspicious_blocked = 0
            for ip, endpoint, user_agent in suspicious_requests:
                allowed, message, action = await ddos.check_request(ip, endpoint, user_agent)
                if not allowed:
                    suspicious_blocked += 1
            
            # Тест 3: Rate limiting
            rate_limit_test_ip = "192.168.1.200"
            rate_limited = 0
            for i in range(150):  # Превышаем лимит
                allowed, message, action = await ddos.check_request(rate_limit_test_ip, "/api/test", "Mozilla/5.0")
                if not allowed and "rate" in message.lower():
                    rate_limited += 1
                    break
            
            # Результаты
            ddos_score = (normal_passed / len(normal_requests)) * 0.4 + \
                        (suspicious_blocked / len(suspicious_requests)) * 0.4 + \
                        (1 if rate_limited > 0 else 0) * 0.2
            
            self.test_results.append({
                "system": "DDoS Protection",
                "score": ddos_score,
                "details": {
                    "normal_requests_passed": f"{normal_passed}/{len(normal_requests)}",
                    "suspicious_requests_blocked": f"{suspicious_blocked}/{len(suspicious_requests)}",
                    "rate_limiting_working": rate_limited > 0,
                    "statistics": ddos.get_statistics()
                },
                "status": "PASS" if ddos_score >= 0.8 else "FAIL"
            })
            
            print(f"  ✅ Normal requests: {normal_passed}/{len(normal_requests)}")
            print(f"  ✅ Suspicious blocked: {suspicious_blocked}/{len(suspicious_requests)}")
            print(f"  ✅ Rate limiting: {'Working' if rate_limited > 0 else 'Not working'}")
            print(f"  📊 Score: {ddos_score:.2f}")
            
        except Exception as e:
            self.test_results.append({
                "system": "DDoS Protection",
                "score": 0,
                "error": str(e),
                "status": "ERROR"
            })
            print(f"  ❌ Error: {e}")
    
    async def test_rate_limiting(self):
        """Тестирование Rate Limiting"""
        print("\n⏱️ Testing Rate Limiting System...")
        
        try:
            rate_limiter = AdvancedRateLimiter()
            
            # Тест 1: Нормальные запросы
            normal_requests = [
                ("192.168.1.1", "/api/v1/status", 1),
                ("192.168.1.2", "/vpn/servers", 1),
                ("192.168.1.3", "/admin/dashboard", 1)
            ]
            
            normal_passed = 0
            for ip, endpoint, tokens in normal_requests:
                result = await rate_limiter.check_rate_limit(ip, endpoint, tokens)
                if result.allowed:
                    normal_passed += 1
            
            # Тест 2: Превышение лимитов
            rate_limit_test_ip = "192.168.1.300"
            rate_limited = 0
            for i in range(200):  # Превышаем лимит
                result = await rate_limiter.check_rate_limit(rate_limit_test_ip, "/api/test", 1)
                if not result.allowed:
                    rate_limited += 1
                    break
            
            # Тест 3: Разные стратегии
            strategies_tested = 0
            for rule in rate_limiter.rules:
                if rule.strategy.value in ["fixed_window", "sliding_window", "token_bucket", "leaky_bucket"]:
                    strategies_tested += 1
            
            # Результаты
            rate_score = (normal_passed / len(normal_requests)) * 0.4 + \
                        (1 if rate_limited > 0 else 0) * 0.4 + \
                        (strategies_tested / 4) * 0.2
            
            self.test_results.append({
                "system": "Rate Limiting",
                "score": rate_score,
                "details": {
                    "normal_requests_passed": f"{normal_passed}/{len(normal_requests)}",
                    "rate_limiting_working": rate_limited > 0,
                    "strategies_tested": strategies_tested,
                    "metrics": rate_limiter.get_metrics()
                },
                "status": "PASS" if rate_score >= 0.8 else "FAIL"
            })
            
            print(f"  ✅ Normal requests: {normal_passed}/{len(normal_requests)}")
            print(f"  ✅ Rate limiting: {'Working' if rate_limited > 0 else 'Not working'}")
            print(f"  ✅ Strategies: {strategies_tested}/4")
            print(f"  📊 Score: {rate_score:.2f}")
            
        except Exception as e:
            self.test_results.append({
                "system": "Rate Limiting",
                "score": 0,
                "error": str(e),
                "status": "ERROR"
            })
            print(f"  ❌ Error: {e}")
    
    async def test_intrusion_detection(self):
        """Тестирование системы обнаружения вторжений"""
        print("\n🛡️ Testing Intrusion Detection System...")
        
        try:
            ids = IntrusionDetectionSystem()
            
            # Тест 1: Нормальные запросы
            normal_requests = [
                ("192.168.1.1", "Mozilla/5.0", "/api/v1/status", "GET", ""),
                ("192.168.1.2", "Mozilla/5.0", "/vpn/servers", "GET", ""),
                ("192.168.1.3", "Mozilla/5.0", "/admin/dashboard", "GET", "")
            ]
            
            normal_safe = 0
            for ip, user_agent, endpoint, method, payload in normal_requests:
                safe, threats = await ids.analyze_request(ip, user_agent, endpoint, method, payload)
                if safe:
                    normal_safe += 1
            
            # Тест 2: Атаки
            attack_requests = [
                ("192.168.1.100", "sqlmap", "/login", "POST", "admin' OR '1'='1"),
                ("192.168.1.101", "scanner", "/admin/backup", "GET", ""),
                ("192.168.1.102", "bot", "/.env", "GET", ""),
                ("192.168.1.103", "hacker", "/api/users", "GET", "<script>alert('xss')</script>")
            ]
            
            attacks_detected = 0
            for ip, user_agent, endpoint, method, payload in attack_requests:
                safe, threats = await ids.analyze_request(ip, user_agent, endpoint, method, payload)
                if not safe and len(threats) > 0:
                    attacks_detected += 1
            
            # Тест 3: Honeypot endpoints
            honeypot_requests = [
                ("192.168.1.200", "scanner", "/admin/backup", "GET", ""),
                ("192.168.1.201", "bot", "/.env", "GET", ""),
                ("192.168.1.202", "hacker", "/phpmyadmin", "GET", "")
            ]
            
            honeypot_detected = 0
            for ip, user_agent, endpoint, method, payload in honeypot_requests:
                safe, threats = await ids.analyze_request(ip, user_agent, endpoint, method, payload)
                if not safe:
                    for threat in threats:
                        if threat.threat_type.value == "honeypot_access":
                            honeypot_detected += 1
                            break
            
            # Результаты
            ids_score = (normal_safe / len(normal_requests)) * 0.3 + \
                       (attacks_detected / len(attack_requests)) * 0.4 + \
                       (honeypot_detected / len(honeypot_requests)) * 0.3
            
            self.test_results.append({
                "system": "Intrusion Detection",
                "score": ids_score,
                "details": {
                    "normal_requests_safe": f"{normal_safe}/{len(normal_requests)}",
                    "attacks_detected": f"{attacks_detected}/{len(attack_requests)}",
                    "honeypot_detected": f"{honeypot_detected}/{len(honeypot_requests)}",
                    "statistics": ids.get_statistics()
                },
                "status": "PASS" if ids_score >= 0.8 else "FAIL"
            })
            
            print(f"  ✅ Normal requests safe: {normal_safe}/{len(normal_requests)}")
            print(f"  ✅ Attacks detected: {attacks_detected}/{len(attack_requests)}")
            print(f"  ✅ Honeypot detected: {honeypot_detected}/{len(honeypot_requests)}")
            print(f"  📊 Score: {ids_score:.2f}")
            
        except Exception as e:
            self.test_results.append({
                "system": "Intrusion Detection",
                "score": 0,
                "error": str(e),
                "status": "ERROR"
            })
            print(f"  ❌ Error: {e}")
    
    async def test_audit_logging(self):
        """Тестирование системы аудита"""
        print("\n📝 Testing Audit Logging System...")
        
        try:
            audit_logger = SecurityAuditLogger()
            
            # Тест 1: Логирование событий
            test_events = [
                (EventType.AUTHENTICATION, "User login successful", "user123", "192.168.1.1"),
                (EventType.VPN_OPERATION, "VPN connection established", "user123", "192.168.1.1"),
                (EventType.SECURITY, "Suspicious activity detected", None, "192.168.1.100"),
                (EventType.ADMIN_ACTION, "Configuration changed", "admin", "192.168.1.10"),
                (EventType.ERROR, "Database connection failed", None, None)
            ]
            
            events_logged = 0
            for event_type, message, user_id, ip_address in test_events:
                event_id = log_audit_event(
                    event_type=event_type,
                    message=message,
                    user_id=user_id,
                    ip_address=ip_address,
                    endpoint="/api/test",
                    method="POST",
                    status_code=200
                )
                if event_id:
                    events_logged += 1
            
            # Тест 2: Получение событий
            events = audit_logger.get_events(limit=10)
            events_retrieved = len(events)
            
            # Тест 3: Статистика
            stats = audit_logger.get_statistics()
            stats_available = len(stats) > 0
            
            # Результаты
            audit_score = (events_logged / len(test_events)) * 0.5 + \
                         (1 if events_retrieved > 0 else 0) * 0.3 + \
                         (1 if stats_available else 0) * 0.2
            
            self.test_results.append({
                "system": "Audit Logging",
                "score": audit_score,
                "details": {
                    "events_logged": f"{events_logged}/{len(test_events)}",
                    "events_retrieved": events_retrieved,
                    "statistics_available": stats_available,
                    "statistics": stats
                },
                "status": "PASS" if audit_score >= 0.8 else "FAIL"
            })
            
            print(f"  ✅ Events logged: {events_logged}/{len(test_events)}")
            print(f"  ✅ Events retrieved: {events_retrieved}")
            print(f"  ✅ Statistics available: {stats_available}")
            print(f"  📊 Score: {audit_score:.2f}")
            
        except Exception as e:
            self.test_results.append({
                "system": "Audit Logging",
                "score": 0,
                "error": str(e),
                "status": "ERROR"
            })
            print(f"  ❌ Error: {e}")
    
    async def test_two_factor_auth(self):
        """Тестирование двухфакторной аутентификации"""
        print("\n🔐 Testing Two-Factor Authentication System...")
        
        try:
            two_fa = TwoFactorAuth()
            
            # Тест 1: Настройка 2FA
            user_id = "test_user_123"
            methods = [AuthMethod.TOTP, AuthMethod.BACKUP_CODE, AuthMethod.EMAIL]
            
            setup_result = setup_user_2fa(
                user_id=user_id,
                methods=methods,
                email="test@aladdin-vpn.com"
            )
            
            setup_success = "error" not in setup_result and setup_result.get("enabled", False)
            
            # Тест 2: Проверка эндпоинтов
            test_endpoints = [
                "/admin/dashboard",
                "/vpn/connect",
                "/api/status",
                "/config/download"
            ]
            
            endpoints_checked = 0
            for endpoint in test_endpoints:
                required = two_fa.is_2fa_required(endpoint)
                if isinstance(required, bool):
                    endpoints_checked += 1
            
            # Тест 3: Статистика
            stats = two_fa.get_statistics()
            stats_available = len(stats) > 0
            
            # Результаты
            two_fa_score = (1 if setup_success else 0) * 0.5 + \
                          (endpoints_checked / len(test_endpoints)) * 0.3 + \
                          (1 if stats_available else 0) * 0.2
            
            self.test_results.append({
                "system": "Two-Factor Authentication",
                "score": two_fa_score,
                "details": {
                    "setup_success": setup_success,
                    "endpoints_checked": f"{endpoints_checked}/{len(test_endpoints)}",
                    "statistics_available": stats_available,
                    "statistics": stats
                },
                "status": "PASS" if two_fa_score >= 0.8 else "FAIL"
            })
            
            print(f"  ✅ Setup success: {setup_success}")
            print(f"  ✅ Endpoints checked: {endpoints_checked}/{len(test_endpoints)}")
            print(f"  ✅ Statistics available: {stats_available}")
            print(f"  📊 Score: {two_fa_score:.2f}")
            
        except Exception as e:
            self.test_results.append({
                "system": "Two-Factor Authentication",
                "score": 0,
                "error": str(e),
                "status": "ERROR"
            })
            print(f"  ❌ Error: {e}")
    
    async def test_security_integration(self):
        """Тестирование интеграции безопасности"""
        print("\n🔗 Testing Security Integration...")
        
        try:
            # Тест 1: Комплексная проверка безопасности
            test_requests = [
                ("192.168.1.1", "Mozilla/5.0", "/api/v1/status", "GET", "", None, "user123", "session123"),
                ("192.168.1.2", "sqlmap", "/admin/login", "POST", "admin' OR '1'='1", None, None, None),
                ("192.168.1.3", "scanner", "/admin/backup", "GET", "", None, None, None),
                ("192.168.1.4", "Mozilla/5.0", "/vpn/connect", "POST", "", None, "user456", "session456"),
            ]
            
            integration_tests = 0
            for ip, user_agent, endpoint, method, payload, headers, user_id, session_id in test_requests:
                result = await check_security(ip, user_agent, endpoint, method, payload, headers, user_id, session_id)
                if result and hasattr(result, 'allowed'):
                    integration_tests += 1
            
            # Тест 2: Дашборд безопасности
            dashboard = await get_security_dashboard()
            dashboard_available = "error" not in dashboard
            
            # Тест 3: Статус систем
            status = get_security_status()
            status_available = len(status) > 0
            
            # Результаты
            integration_score = (integration_tests / len(test_requests)) * 0.5 + \
                               (1 if dashboard_available else 0) * 0.3 + \
                               (1 if status_available else 0) * 0.2
            
            self.test_results.append({
                "system": "Security Integration",
                "score": integration_score,
                "details": {
                    "integration_tests": f"{integration_tests}/{len(test_requests)}",
                    "dashboard_available": dashboard_available,
                    "status_available": status_available,
                    "dashboard": dashboard if dashboard_available else None
                },
                "status": "PASS" if integration_score >= 0.8 else "FAIL"
            })
            
            print(f"  ✅ Integration tests: {integration_tests}/{len(test_requests)}")
            print(f"  ✅ Dashboard available: {dashboard_available}")
            print(f"  ✅ Status available: {status_available}")
            print(f"  📊 Score: {integration_score:.2f}")
            
        except Exception as e:
            self.test_results.append({
                "system": "Security Integration",
                "score": 0,
                "error": str(e),
                "status": "ERROR"
            })
            print(f"  ❌ Error: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Генерация отчета о тестировании"""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()
        
        # Подсчет результатов
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        # Общий балл
        total_score = sum(r["score"] for r in self.test_results if "score" in r)
        average_score = total_score / total_tests if total_tests > 0 else 0
        
        # Оценка безопасности
        if average_score >= 0.9:
            security_grade = "A+"
            security_status = "EXCELLENT"
        elif average_score >= 0.8:
            security_grade = "A"
            security_status = "GOOD"
        elif average_score >= 0.7:
            security_grade = "B"
            security_status = "ACCEPTABLE"
        elif average_score >= 0.6:
            security_grade = "C"
            security_status = "NEEDS_IMPROVEMENT"
        else:
            security_grade = "D"
            security_status = "POOR"
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
            },
            "security_assessment": {
                "overall_score": f"{average_score:.2f}",
                "security_grade": security_grade,
                "security_status": security_status,
                "recommendation": self._get_recommendation(average_score)
            },
            "test_results": self.test_results,
            "execution_info": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "test_version": "1.0.0"
            }
        }
        
        return report
    
    def _get_recommendation(self, score: float) -> str:
        """Получение рекомендации на основе балла"""
        if score >= 0.9:
            return "Security systems are working excellently. Continue monitoring and regular testing."
        elif score >= 0.8:
            return "Security systems are working well. Consider minor improvements and regular updates."
        elif score >= 0.7:
            return "Security systems are acceptable but need improvement. Review failed tests and fix issues."
        elif score >= 0.6:
            return "Security systems need significant improvement. Address critical issues immediately."
        else:
            return "Security systems are inadequate. Immediate action required to fix critical vulnerabilities."
    
    def save_report(self, report: Dict[str, Any]) -> None:
        """Сохранение отчета"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_test_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Report saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")


async def main():
    """Главная функция тестирования"""
    test_suite = SecurityTestSuite()
    report = await test_suite.run_all_tests()
    
    # Вывод итогового отчета
    print("\n" + "=" * 60)
    print("📊 SECURITY TEST REPORT")
    print("=" * 60)
    
    summary = report["test_summary"]
    assessment = report["security_assessment"]
    
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Errors: {summary['errors']}")
    print(f"Success Rate: {summary['success_rate']}")
    print()
    print(f"Overall Score: {assessment['overall_score']}")
    print(f"Security Grade: {assessment['security_grade']}")
    print(f"Status: {assessment['security_status']}")
    print()
    print(f"Recommendation: {assessment['recommendation']}")
    
    return report


if __name__ == "__main__":
    # Запуск тестов
    asyncio.run(main())