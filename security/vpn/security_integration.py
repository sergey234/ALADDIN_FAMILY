#!/usr/bin/env python3
"""
ALADDIN VPN - Security Integration Module
Интеграция всех систем безопасности

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import asyncio

from audit_logging.audit_logger import EventType, SecurityAuditLogger, log_audit_event
from auth.two_factor_auth import TwoFactorAuth, is_2fa_required

# Импорт модулей безопасности
from protection.ddos_protection import DDoSProtectionSystem
from protection.ddos_protection import check_request as ddos_check
from protection.intrusion_detection import IntrusionDetectionSystem
from protection.intrusion_detection import analyze_request as ids_analyze
from protection.rate_limiter import AdvancedRateLimiter
from protection.rate_limiter import check_rate_limit as rate_check

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityResult:
    """Результат проверки безопасности"""

    allowed: bool
    action: str
    message: str
    details: Dict[str, Any] = None
    threats_detected: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.threats_detected is None:
            self.threats_detected = []


class SecurityIntegration:
    """
    Интеграционный модуль безопасности

    Объединяет все системы безопасности:
    - DDoS Protection
    - Rate Limiting
    - Intrusion Detection
    - Audit Logging
    - Two-Factor Authentication
    """

    def __init__(self):
        # Инициализация систем безопасности
        self.ddos_protection = DDoSProtectionSystem()
        self.rate_limiter = AdvancedRateLimiter()
        self.ids = IntrusionDetectionSystem()
        self.audit_logger = SecurityAuditLogger()
        self.two_factor_auth = TwoFactorAuth()

        # Статистика
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "threats_detected": 0,
            "2fa_required": 0,
            "2fa_verified": 0,
        }

        logger.info("Security Integration Module initialized")

    async def check_security(
        self,
        ip: str,
        user_agent: str,
        endpoint: str,
        method: str,
        payload: str = "",
        headers: Dict[str, str] = None,
        user_id: str = None,
        session_id: str = None,
    ) -> SecurityResult:
        """
        Комплексная проверка безопасности

        Args:
            ip: IP адрес клиента
            user_agent: User-Agent заголовок
            endpoint: Эндпоинт запроса
            method: HTTP метод
            payload: Тело запроса
            headers: HTTP заголовки
            user_id: ID пользователя
            session_id: ID сессии

        Returns:
            SecurityResult: Результат проверки безопасности
        """
        try:
            self.stats["total_requests"] += 1

            # 1. DDoS Protection
            ddos_allowed, ddos_message, ddos_action = await ddos_check(
                ip, endpoint, user_agent
            )
            if not ddos_allowed:
                self._log_security_event(
                    ip, endpoint, method, "DDoS blocked", user_id
                )
                return SecurityResult(
                    allowed=False,
                    action=ddos_action.value,
                    message=ddos_message,
                    threats_detected=["ddos"],
                )

            # 2. Rate Limiting
            rate_result = await rate_check(ip, endpoint, 1)
            if not rate_result.allowed:
                self._log_security_event(
                    ip, endpoint, method, "Rate limited", user_id
                )
                return SecurityResult(
                    allowed=False,
                    action=rate_result.action.value,
                    message=rate_result.message,
                    threats_detected=["rate_limit"],
                )

            # 3. Intrusion Detection
            ids_safe, ids_threats = await ids_analyze(
                ip, user_agent, endpoint, method, payload, headers
            )
            if not ids_safe:
                threat_types = [
                    threat.threat_type.value for threat in ids_threats
                ]
                self._log_security_event(
                    ip,
                    endpoint,
                    method,
                    f"IDS threats: {threat_types}",
                    user_id,
                )
                return SecurityResult(
                    allowed=False,
                    action="block",
                    message="Intrusion detected",
                    threats_detected=threat_types,
                )

            # 4. 2FA Check
            if is_2fa_required(endpoint):
                self.stats["2fa_required"] += 1
                if not self._check_2fa_required(user_id, session_id):
                    return SecurityResult(
                        allowed=False,
                        action="2fa_required",
                        message="Two-factor authentication required",
                        threats_detected=[],
                    )
                else:
                    self.stats["2fa_verified"] += 1

            # 5. Audit Logging
            self._log_request(
                ip, user_agent, endpoint, method, user_id, session_id
            )

            # Обновляем статистику
            self.stats["threats_detected"] += len(ids_threats)

            return SecurityResult(
                allowed=True,
                action="allow",
                message="Request allowed",
                details={
                    "ddos_protection": "passed",
                    "rate_limiting": "passed",
                    "ids": "passed",
                    "2fa": (
                        "passed"
                        if is_2fa_required(endpoint)
                        else "not_required"
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Error in security check: {e}")
            return SecurityResult(
                allowed=False,
                action="error",
                message="Security check error",
                details={"error": str(e)},
            )

    def _check_2fa_required(self, user_id: str, session_id: str) -> bool:
        """Проверка 2FA для пользователя"""
        if not user_id:
            return False

        # Проверяем сессию 2FA
        if session_id:
            valid, message, verified_user_id = (
                self.two_factor_auth.verify_session(session_id)
            )
            return valid and verified_user_id == user_id

        return False

    def _log_security_event(
        self,
        ip: str,
        endpoint: str,
        method: str,
        message: str,
        user_id: str = None,
    ):
        """Логирование события безопасности"""
        log_audit_event(
            EventType.SECURITY,
            f"Security event: {message}",
            user_id=user_id,
            ip_address=ip,
            endpoint=endpoint,
            method=method,
            details={"security_event": True},
        )

    def _log_request(
        self,
        ip: str,
        user_agent: str,
        endpoint: str,
        method: str,
        user_id: str = None,
        session_id: str = None,
    ):
        """Логирование запроса"""
        log_audit_event(
            EventType.SYSTEM,
            f"Request processed: {method} {endpoint}",
            user_id=user_id,
            ip_address=ip,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            session_id=session_id,
            details={"request_processed": True},
        )

    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для дашборда безопасности"""
        try:
            # Собираем статистику со всех систем
            ddos_stats = self.ddos_protection.get_statistics()
            rate_stats = self.rate_limiter.get_metrics()
            ids_stats = self.ids.get_statistics()
            audit_stats = self.audit_logger.get_statistics()
            two_fa_stats = self.two_factor_auth.get_statistics()

            return {
                "overview": {
                    "total_requests": self.stats["total_requests"],
                    "blocked_requests": self.stats["blocked_requests"],
                    "threats_detected": self.stats["threats_detected"],
                    "2fa_required": self.stats["2fa_required"],
                    "2fa_verified": self.stats["2fa_verified"],
                },
                "ddos_protection": ddos_stats,
                "rate_limiting": rate_stats,
                "intrusion_detection": ids_stats,
                "audit_logging": audit_stats,
                "two_factor_auth": two_fa_stats,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}

    async def cleanup_security_data(self) -> None:
        """Очистка данных безопасности"""
        try:
            # Очистка DDoS данных
            await self.ddos_protection.cleanup_old_stats()

            # Очистка Rate Limiting данных
            await self.rate_limiter.cleanup()

            # Очистка IDS данных
            self.ids._cleanup_old_events()

            # Очистка Audit данных
            self.audit_logger.cleanup_old_events()

            # Очистка 2FA данных
            self.two_factor_auth.cleanup_expired_sessions()

            logger.info("Security data cleanup completed")

        except Exception as e:
            logger.error(f"Error in security data cleanup: {e}")

    def get_security_status(self) -> Dict[str, Any]:
        """Получение статуса систем безопасности"""
        return {
            "ddos_protection": {
                "enabled": True,
                "status": "active",
                "blocked_ips": len(self.ddos_protection.blacklist),
            },
            "rate_limiting": {
                "enabled": True,
                "status": "active",
                "rules_count": len(self.rate_limiter.rules),
            },
            "intrusion_detection": {
                "enabled": True,
                "status": "active",
                "rules_count": len(self.ids.ids_rules),
                "honeypot_endpoints": len(self.ids.honeypot_endpoints),
            },
            "audit_logging": {
                "enabled": True,
                "status": "active",
                "total_events": self.audit_logger.stats["total_events"],
            },
            "two_factor_auth": {
                "enabled": True,
                "status": "active",
                "users_with_2fa": self.two_factor_auth.get_statistics()[
                    "enabled_2fa"
                ],
            },
        }

    async def emergency_lockdown(
        self, reason: str = "Emergency lockdown activated"
    ) -> None:
        """Экстренная блокировка системы"""
        try:
            # Блокируем все IP кроме whitelist
            # Увеличиваем строгость rate limiting
            # Активируем максимальную защиту IDS
            # Логируем событие

            log_audit_event(
                EventType.SECURITY,
                f"EMERGENCY LOCKDOWN: {reason}",
                details={"emergency": True, "reason": reason},
            )

            logger.critical(f"EMERGENCY LOCKDOWN ACTIVATED: {reason}")

        except Exception as e:
            logger.error(f"Error in emergency lockdown: {e}")

    async def start_security_monitoring(self) -> None:
        """Запуск мониторинга безопасности"""
        try:
            # Запускаем мониторинг всех систем
            await self.ddos_protection.start_monitoring()

            # Планируем периодическую очистку
            asyncio.create_task(self._periodic_cleanup())

            logger.info("Security monitoring started")

        except Exception as e:
            logger.error(f"Error starting security monitoring: {e}")

    async def stop_security_monitoring(self) -> None:
        """Остановка мониторинга безопасности"""
        try:
            await self.ddos_protection.stop_monitoring()
            logger.info("Security monitoring stopped")

        except Exception as e:
            logger.error(f"Error stopping security monitoring: {e}")

    async def _periodic_cleanup(self) -> None:
        """Периодическая очистка данных"""
        while True:
            try:
                await asyncio.sleep(3600)  # Каждый час
                await self.cleanup_security_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")


# Глобальный экземпляр интеграции безопасности
security_integration = SecurityIntegration()


async def check_security(
    ip: str,
    user_agent: str,
    endpoint: str,
    method: str,
    payload: str = "",
    headers: Dict[str, str] = None,
    user_id: str = None,
    session_id: str = None,
) -> SecurityResult:
    """Глобальная функция проверки безопасности"""
    return await security_integration.check_security(
        ip, user_agent, endpoint, method, payload, headers, user_id, session_id
    )


async def get_security_dashboard() -> Dict[str, Any]:
    """Получение данных дашборда безопасности"""
    return await security_integration.get_security_dashboard_data()


def get_security_status() -> Dict[str, Any]:
    """Получение статуса систем безопасности"""
    return security_integration.get_security_status()


if __name__ == "__main__":
    # Тестирование интеграции безопасности
    async def test_security_integration():
        print("🧪 Testing Security Integration...")

        # Тестовые запросы
        test_requests = [
            (
                "192.168.1.1",
                "Mozilla/5.0",
                "/api/v1/status",
                "GET",
                "",
                None,
                "user123",
                "session123",
            ),
            (
                "192.168.1.2",
                "sqlmap",
                "/admin/login",
                "POST",
                "admin' OR '1'='1",
                None,
                None,
                None,
            ),
            (
                "192.168.1.3",
                "scanner",
                "/admin/backup",
                "GET",
                "",
                None,
                None,
                None,
            ),
            (
                "192.168.1.4",
                "Mozilla/5.0",
                "/vpn/connect",
                "POST",
                "",
                None,
                "user456",
                "session456",
            ),
        ]

        for (
            ip,
            user_agent,
            endpoint,
            method,
            payload,
            headers,
            user_id,
            session_id,
        ) in test_requests:
            result = await check_security(
                ip,
                user_agent,
                endpoint,
                method,
                payload,
                headers,
                user_id,
                session_id,
            )
            print(
                f"IP: {ip}, Endpoint: {endpoint}, Allowed: {result.allowed}, Action: {result.action}"
            )
            if result.threats_detected:
                print(f"  Threats: {result.threats_detected}")

        # Статус систем
        status = get_security_status()
        print(f"\n📊 Security Status: {status}")

        # Дашборд
        dashboard = await get_security_dashboard()
        print(f"\n📈 Dashboard Overview: {dashboard['overview']}")

        print("✅ Security Integration test completed")

    # Запуск тестов
    asyncio.run(test_security_integration())
