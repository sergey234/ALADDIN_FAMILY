#!/usr/bin/env python3
"""
ALADDIN VPN - Intrusion Detection System (IDS)
Система обнаружения вторжений и honeypot endpoints

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import hashlib
import ipaddress
import json
import logging
import random
import re
import string
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatType(Enum):
    """Типы угроз"""

    SCANNING = "scanning"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    DDOS = "ddos"
    MALWARE = "malware"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    HONEYPOT_ACCESS = "honeypot_access"


class Severity(Enum):
    """Уровни серьезности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Action(Enum):
    """Действия при обнаружении угрозы"""

    LOG = "log"
    ALERT = "alert"
    BLOCK = "block"
    CAPTCHA = "captcha"
    HONEYPOT = "honeypot"
    QUARANTINE = "quarantine"


@dataclass
class ThreatEvent:
    """Событие угрозы"""

    event_id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: Severity
    source_ip: str
    user_agent: str
    endpoint: str
    method: str
    payload: str
    description: str
    confidence: float
    action_taken: Action
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class IDSRule:
    """Правило IDS"""

    rule_id: str
    name: str
    pattern: str
    threat_type: ThreatType
    severity: Severity
    action: Action
    enabled: bool = True
    threshold: int = 1
    time_window: int = 300  # секунды
    description: str = ""


@dataclass
class HoneypotEndpoint:
    """Honeypot эндпоинт"""

    path: str
    method: str
    response_delay: float = 0.5
    fake_data: Dict[str, Any] = None
    log_access: bool = True
    alert_on_access: bool = True

    def __post_init__(self):
        if self.fake_data is None:
            self.fake_data = {}


class IntrusionDetectionSystem:
    """
    Система обнаружения вторжений

    Функции:
    - Обнаружение сканирования портов
    - Защита от brute force атак
    - Обнаружение SQL injection
    - Обнаружение XSS атак
    - Path traversal защита
    - Command injection защита
    - Honeypot endpoints
    - Поведенческий анализ
    - Корреляция событий
    """

    def __init__(self, config_file: str = "config/ids_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

        # Хранилища данных
        self.threat_events: List[ThreatEvent] = []
        self.ids_rules: List[IDSRule] = []
        self.honeypot_endpoints: List[HoneypotEndpoint] = []
        self.ip_behavior: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.blocked_ips: Set[str] = set()
        self.quarantined_ips: Set[str] = set()

        # Статистика
        self.stats = {
            "total_threats": 0,
            "threats_by_type": defaultdict(int),
            "threats_by_severity": defaultdict(int),
            "blocked_ips": 0,
            "honeypot_accesses": 0,
        }

        # Инициализация
        self._load_rules()
        self._setup_honeypots()

        logger.info("Intrusion Detection System initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            "enabled": True,
            "rules": {
                "scanning_detection": True,
                "brute_force_detection": True,
                "injection_detection": True,
                "behavioral_analysis": True,
                "honeypot_enabled": True,
            },
            "thresholds": {
                "max_requests_per_minute": 100,
                "max_failed_logins": 5,
                "max_scan_attempts": 10,
                "suspicious_pattern_threshold": 3,
            },
            "actions": {
                "auto_block": True,
                "alert_on_high_severity": True,
                "quarantine_suspicious": True,
                "log_all_events": True,
            },
            "honeypot": {
                "enabled": True,
                "endpoints": [
                    "/admin/backup",
                    "/admin/export",
                    "/.env",
                    "/config/database",
                    "/logs/access.log",
                    "/api/v1/users",
                    "/api/v1/passwords",
                    "/phpmyadmin",
                    "/wp-admin",
                    "/administrator",
                ],
                "response_delay": 0.5,
                "fake_data": {
                    "users": ["admin", "root", "administrator"],
                    "passwords": ["admin", "password", "123456"],
                    "files": ["backup.sql", "config.ini", "users.db"],
                },
            },
            "monitoring": {"enabled": True, "alert_email": "", "alert_webhook": "", "retention_days": 30},
        }

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self._save_config(default_config)

        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        import os

        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _load_rules(self) -> None:
        """Загрузка правил IDS"""
        default_rules = [
            # SQL Injection правила
            IDSRule(
                rule_id="sql_injection_1",
                name="SQL Injection - Basic",
                pattern=r"(union|select|insert|update|delete|drop|create|alter|exec|execute).*from",
                threat_type=ThreatType.SQL_INJECTION,
                severity=Severity.HIGH,
                action=Action.BLOCK,
                description="Basic SQL injection patterns",
            ),
            IDSRule(
                rule_id="sql_injection_2",
                name="SQL Injection - Advanced",
                pattern=r"('|(\\')|(;)|(\\;)|(--)|(\\*)|(\\|))",
                threat_type=ThreatType.SQL_INJECTION,
                severity=Severity.HIGH,
                action=Action.BLOCK,
                description="Advanced SQL injection patterns",
            ),
            # XSS правила
            IDSRule(
                rule_id="xss_1",
                name="XSS - Script Tags",
                pattern=r"<script[^>]*>.*</script>",
                threat_type=ThreatType.XSS,
                severity=Severity.MEDIUM,
                action=Action.BLOCK,
                description="Script tag XSS attempts",
            ),
            IDSRule(
                rule_id="xss_2",
                name="XSS - Event Handlers",
                pattern=r"on\w+\s*=",
                threat_type=ThreatType.XSS,
                severity=Severity.MEDIUM,
                action=Action.BLOCK,
                description="Event handler XSS attempts",
            ),
            # Path Traversal правила
            IDSRule(
                rule_id="path_traversal_1",
                name="Path Traversal - Basic",
                pattern=r"\.\./|\.\.\\\\",
                threat_type=ThreatType.PATH_TRAVERSAL,
                severity=Severity.HIGH,
                action=Action.BLOCK,
                description="Basic path traversal attempts",
            ),
            IDSRule(
                rule_id="path_traversal_2",
                name="Path Traversal - Encoded",
                pattern=r"(%2e%2e%2f|%2e%2e%5c|%252e%252e%252f)",
                threat_type=ThreatType.PATH_TRAVERSAL,
                severity=Severity.HIGH,
                action=Action.BLOCK,
                description="Encoded path traversal attempts",
            ),
            # Command Injection правила
            IDSRule(
                rule_id="command_injection_1",
                name="Command Injection - Basic",
                pattern=r"[;&|`$()]",
                threat_type=ThreatType.COMMAND_INJECTION,
                severity=Severity.HIGH,
                action=Action.BLOCK,
                description="Basic command injection patterns",
            ),
            IDSRule(
                rule_id="command_injection_2",
                name="Command Injection - Advanced",
                pattern=r"(cat|ls|dir|type|more|less|head|tail|grep|find|wget|curl|nc|netcat)",
                threat_type=ThreatType.COMMAND_INJECTION,
                severity=Severity.HIGH,
                action=Action.BLOCK,
                description="Advanced command injection patterns",
            ),
            # Brute Force правила
            IDSRule(
                rule_id="brute_force_1",
                name="Brute Force - Login",
                pattern=r"/login|/auth|/signin",
                threat_type=ThreatType.BRUTE_FORCE,
                severity=Severity.MEDIUM,
                action=Action.ALERT,
                threshold=5,
                time_window=300,
                description="Multiple login attempts",
            ),
            # Scanning правила
            IDSRule(
                rule_id="scanning_1",
                name="Port Scanning",
                pattern=r"/(admin|phpmyadmin|wp-admin|administrator|manager|login)",
                threat_type=ThreatType.SCANNING,
                severity=Severity.MEDIUM,
                action=Action.ALERT,
                threshold=10,
                time_window=600,
                description="Administrative interface scanning",
            ),
            # Malware правила
            IDSRule(
                rule_id="malware_1",
                name="Malware - Common Patterns",
                pattern=r"(eval|base64_decode|gzinflate|str_rot13|create_function)",
                threat_type=ThreatType.MALWARE,
                severity=Severity.CRITICAL,
                action=Action.BLOCK,
                description="Common malware patterns",
            ),
        ]

        self.ids_rules = default_rules.copy()

        # Загружаем кастомные правила из конфига
        if "custom_rules" in self.config:
            for rule_data in self.config["custom_rules"]:
                rule = IDSRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    pattern=rule_data["pattern"],
                    threat_type=ThreatType(rule_data["threat_type"]),
                    severity=Severity(rule_data["severity"]),
                    action=Action(rule_data["action"]),
                    enabled=rule_data.get("enabled", True),
                    threshold=rule_data.get("threshold", 1),
                    time_window=rule_data.get("time_window", 300),
                    description=rule_data.get("description", ""),
                )
                self.ids_rules.append(rule)

    def _setup_honeypots(self) -> None:
        """Настройка honeypot эндпоинтов"""
        if not self.config.get("honeypot", {}).get("enabled", True):
            return

        honeypot_endpoints = self.config.get("honeypot", {}).get("endpoints", [])

        for endpoint in honeypot_endpoints:
            honeypot = HoneypotEndpoint(
                path=endpoint,
                method="GET",
                response_delay=self.config.get("honeypot", {}).get("response_delay", 0.5),
                fake_data=self.config.get("honeypot", {}).get("fake_data", {}),
                log_access=True,
                alert_on_access=True,
            )
            self.honeypot_endpoints.append(honeypot)

        logger.info(f"Setup {len(self.honeypot_endpoints)} honeypot endpoints")

    async def analyze_request(
        self, ip: str, user_agent: str, endpoint: str, method: str, payload: str = "", headers: Dict[str, str] = None
    ) -> Tuple[bool, List[ThreatEvent]]:
        """
        Анализ запроса на предмет угроз

        Args:
            ip: IP адрес источника
            user_agent: User-Agent заголовок
            endpoint: Эндпоинт запроса
            method: HTTP метод
            payload: Тело запроса
            headers: HTTP заголовки

        Returns:
            Tuple[bool, List[ThreatEvent]]: (безопасен, список угроз)
        """
        if not self.config.get("enabled", True):
            return True, []

        threats = []

        try:
            # Проверка honeypot эндпоинтов
            honeypot_threat = self._check_honeypot_access(ip, user_agent, endpoint, method)
            if honeypot_threat:
                threats.append(honeypot_threat)

            # Проверка правил IDS
            rule_threats = self._check_ids_rules(ip, user_agent, endpoint, method, payload)
            threats.extend(rule_threats)

            # Поведенческий анализ
            behavior_threats = self._analyze_behavior(ip, user_agent, endpoint, method)
            threats.extend(behavior_threats)

            # Обновление статистики
            for threat in threats:
                self._update_stats(threat)

            # Сохранение событий
            self.threat_events.extend(threats)

            # Очистка старых событий
            self._cleanup_old_events()

            # Принятие мер
            for threat in threats:
                await self._take_action(threat)

            return len(threats) == 0, threats

        except Exception as e:
            logger.error(f"Error analyzing request: {e}")
            return True, []

    def _check_honeypot_access(self, ip: str, user_agent: str, endpoint: str, method: str) -> Optional[ThreatEvent]:
        """Проверка доступа к honeypot эндпоинтам"""
        for honeypot in self.honeypot_endpoints:
            if honeypot.path in endpoint and honeypot.method == method:
                event_id = hashlib.md5(f"{ip}{endpoint}{time.time()}".encode()).hexdigest()[:8]

                threat = ThreatEvent(
                    event_id=event_id,
                    timestamp=datetime.now(timezone.utc),
                    threat_type=ThreatType.HONEYPOT_ACCESS,
                    severity=Severity.HIGH,
                    source_ip=ip,
                    user_agent=user_agent,
                    endpoint=endpoint,
                    method=method,
                    payload="",
                    description=f"Honeypot endpoint accessed: {endpoint}",
                    confidence=1.0,
                    action_taken=Action.LOG,
                    details={"honeypot_path": honeypot.path, "fake_data": honeypot.fake_data},
                )

                self.stats["honeypot_accesses"] += 1
                logger.warning(f"Honeypot accessed by {ip}: {endpoint}")

                return threat

        return None

    def _check_ids_rules(self, ip: str, user_agent: str, endpoint: str, method: str, payload: str) -> List[ThreatEvent]:
        """Проверка правил IDS"""
        threats = []

        for rule in self.ids_rules:
            if not rule.enabled:
                continue

            # Проверяем паттерн
            if re.search(rule.pattern, payload, re.IGNORECASE) or re.search(rule.pattern, endpoint, re.IGNORECASE):
                # Проверяем порог
                if self._check_threshold(ip, rule):
                    event_id = hashlib.md5(f"{ip}{rule.rule_id}{time.time()}".encode()).hexdigest()[:8]

                    threat = ThreatEvent(
                        event_id=event_id,
                        timestamp=datetime.now(timezone.utc),
                        threat_type=rule.threat_type,
                        severity=rule.severity,
                        source_ip=ip,
                        user_agent=user_agent,
                        endpoint=endpoint,
                        method=method,
                        payload=payload,
                        description=f"IDS Rule triggered: {rule.name}",
                        confidence=0.9,
                        action_taken=rule.action,
                        details={"rule_id": rule.rule_id, "pattern": rule.pattern, "threshold": rule.threshold},
                    )

                    threats.append(threat)
                    logger.warning(f"IDS Rule triggered: {rule.name} by {ip}")

        return threats

    def _analyze_behavior(self, ip: str, user_agent: str, endpoint: str, method: str) -> List[ThreatEvent]:
        """Поведенческий анализ"""
        threats = []

        if not self.config.get("rules", {}).get("behavioral_analysis", True):
            return threats

        # Инициализация данных поведения для IP
        if ip not in self.ip_behavior:
            self.ip_behavior[ip] = {
                "requests": deque(maxlen=1000),
                "endpoints": set(),
                "user_agents": set(),
                "first_seen": datetime.now(timezone.utc),
                "last_seen": datetime.now(timezone.utc),
            }

        behavior = self.ip_behavior[ip]
        behavior["requests"].append(
            {"timestamp": datetime.now(timezone.utc), "endpoint": endpoint, "method": method, "user_agent": user_agent}
        )
        behavior["endpoints"].add(endpoint)
        behavior["user_agents"].add(user_agent)
        behavior["last_seen"] = datetime.now(timezone.utc)

        # Анализ сканирования
        if len(behavior["endpoints"]) > 20:
            threat = self._create_behavior_threat(
                ip,
                user_agent,
                endpoint,
                method,
                ThreatType.SCANNING,
                Severity.MEDIUM,
                f"Scanning detected: {len(behavior['endpoints'])} unique endpoints",
            )
            if threat:
                threats.append(threat)

        # Анализ brute force
        recent_requests = [
            r for r in behavior["requests"] if (datetime.now(timezone.utc) - r["timestamp"]).seconds < 300
        ]
        login_attempts = len([r for r in recent_requests if "/login" in r["endpoint"]])

        if login_attempts > 5:
            threat = self._create_behavior_threat(
                ip,
                user_agent,
                endpoint,
                method,
                ThreatType.BRUTE_FORCE,
                Severity.HIGH,
                f"Brute force detected: {login_attempts} login attempts in 5 minutes",
            )
            if threat:
                threats.append(threat)

        # Анализ подозрительного поведения
        if len(behavior["user_agents"]) > 5:
            threat = self._create_behavior_threat(
                ip,
                user_agent,
                endpoint,
                method,
                ThreatType.SUSPICIOUS_BEHAVIOR,
                Severity.MEDIUM,
                f"Suspicious behavior: {len(behavior['user_agents'])} different user agents",
            )
            if threat:
                threats.append(threat)

        return threats

    def _create_behavior_threat(
        self,
        ip: str,
        user_agent: str,
        endpoint: str,
        method: str,
        threat_type: ThreatType,
        severity: Severity,
        description: str,
    ) -> Optional[ThreatEvent]:
        """Создание угрозы на основе поведения"""
        event_id = hashlib.md5(f"{ip}{threat_type.value}{time.time()}".encode()).hexdigest()[:8]

        return ThreatEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            threat_type=threat_type,
            severity=severity,
            source_ip=ip,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            payload="",
            description=description,
            confidence=0.8,
            action_taken=Action.ALERT,
            details={"behavior_analysis": True},
        )

    def _check_threshold(self, ip: str, rule: IDSRule) -> bool:
        """Проверка порога для правила"""
        if rule.threshold <= 1:
            return True

        # Подсчитываем события за временное окно
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=rule.time_window)
        recent_events = [
            e
            for e in self.threat_events
            if (e.source_ip == ip and e.threat_type == rule.threat_type and e.timestamp > cutoff_time)
        ]

        return len(recent_events) >= rule.threshold

    async def _take_action(self, threat: ThreatEvent) -> None:
        """Принятие мер по угрозе"""
        try:
            if threat.action_taken == Action.BLOCK:
                self.blocked_ips.add(threat.source_ip)
                logger.warning(f"IP {threat.source_ip} blocked due to {threat.threat_type.value}")

            elif threat.action_taken == Action.QUARANTINE:
                self.quarantined_ips.add(threat.source_ip)
                logger.warning(f"IP {threat.source_ip} quarantined due to {threat.threat_type.value}")

            elif threat.action_taken == Action.ALERT:
                await self._send_alert(threat)

            elif threat.action_taken == Action.LOG:
                logger.info(f"Threat logged: {threat.description}")

        except Exception as e:
            logger.error(f"Error taking action for threat {threat.event_id}: {e}")

    async def _send_alert(self, threat: ThreatEvent) -> None:
        """Отправка алерта"""
        try:
            alert_data = {
                "timestamp": threat.timestamp.isoformat(),
                "threat_type": threat.threat_type.value,
                "severity": threat.severity.value,
                "source_ip": threat.source_ip,
                "endpoint": threat.endpoint,
                "description": threat.description,
                "confidence": threat.confidence,
            }

            logger.warning(f"IDS ALERT: {json.dumps(alert_data)}")

            # TODO: Реализовать отправку email/webhook

        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    def _update_stats(self, threat: ThreatEvent) -> None:
        """Обновление статистики"""
        self.stats["total_threats"] += 1
        self.stats["threats_by_type"][threat.threat_type.value] += 1
        self.stats["threats_by_severity"][threat.severity.value] += 1

        if threat.action_taken == Action.BLOCK:
            self.stats["blocked_ips"] += 1

    def _cleanup_old_events(self) -> None:
        """Очистка старых событий"""
        retention_days = self.config.get("monitoring", {}).get("retention_days", 30)
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)

        self.threat_events = [e for e in self.threat_events if e.timestamp > cutoff_time]

    def is_ip_blocked(self, ip: str) -> bool:
        """Проверка блокировки IP"""
        return ip in self.blocked_ips

    def is_ip_quarantined(self, ip: str) -> bool:
        """Проверка карантина IP"""
        return ip in self.quarantined_ips

    def unblock_ip(self, ip: str) -> bool:
        """Разблокировка IP"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"IP {ip} unblocked")
            return True
        return False

    def unquarantine_ip(self, ip: str) -> bool:
        """Снятие с карантина IP"""
        if ip in self.quarantined_ips:
            self.quarantined_ips.remove(ip)
            logger.info(f"IP {ip} unquarantined")
            return True
        return False

    def get_threat_events(
        self, ip: str = None, threat_type: ThreatType = None, severity: Severity = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Получение событий угроз"""
        filtered_events = self.threat_events.copy()

        if ip:
            filtered_events = [e for e in filtered_events if e.source_ip == ip]

        if threat_type:
            filtered_events = [e for e in filtered_events if e.threat_type == threat_type]

        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]

        # Сортируем по времени (новые сначала)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)

        # Ограничиваем количество
        filtered_events = filtered_events[:limit]

        # Конвертируем в словари
        return [asdict(event) for event in filtered_events]

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики IDS"""
        return {
            **self.stats,
            "active_rules": len([r for r in self.ids_rules if r.enabled]),
            "honeypot_endpoints": len(self.honeypot_endpoints),
            "blocked_ips_count": len(self.blocked_ips),
            "quarantined_ips_count": len(self.quarantined_ips),
            "monitored_ips": len(self.ip_behavior),
        }

    def add_honeypot_endpoint(
        self, path: str, method: str = "GET", response_delay: float = 0.5, fake_data: Dict[str, Any] = None
    ) -> None:
        """Добавление honeypot эндпоинта"""
        honeypot = HoneypotEndpoint(
            path=path,
            method=method,
            response_delay=response_delay,
            fake_data=fake_data or {},
            log_access=True,
            alert_on_access=True,
        )

        self.honeypot_endpoints.append(honeypot)
        logger.info(f"Added honeypot endpoint: {path}")

    def add_ids_rule(self, rule: IDSRule) -> None:
        """Добавление правила IDS"""
        self.ids_rules.append(rule)
        logger.info(f"Added IDS rule: {rule.name}")


# Глобальный экземпляр IDS
intrusion_detection = IntrusionDetectionSystem()


async def analyze_request(
    ip: str, user_agent: str, endpoint: str, method: str, payload: str = "", headers: Dict[str, str] = None
) -> Tuple[bool, List[ThreatEvent]]:
    """Глобальная функция анализа запроса"""
    return await intrusion_detection.analyze_request(ip, user_agent, endpoint, method, payload, headers)


def is_ip_blocked(ip: str) -> bool:
    """Проверка блокировки IP"""
    return intrusion_detection.is_ip_blocked(ip)


def get_ids_statistics() -> Dict[str, Any]:
    """Получение статистики IDS"""
    return intrusion_detection.get_statistics()


if __name__ == "__main__":
    # Тестирование системы IDS
    async def test_ids():
        print("🧪 Testing Intrusion Detection System...")

        # Тестовые запросы
        test_requests = [
            ("192.168.1.1", "Mozilla/5.0", "/api/v1/status", "GET", ""),
            ("192.168.1.2", "sqlmap", "/login", "POST", "admin' OR '1'='1"),
            ("192.168.1.3", "scanner", "/admin/backup", "GET", ""),
            ("192.168.1.4", "Mozilla/5.0", "/api/v1/users", "GET", ""),
            ("192.168.1.5", "bot", "/.env", "GET", ""),
        ]

        for ip, user_agent, endpoint, method, payload in test_requests:
            safe, threats = await analyze_request(ip, user_agent, endpoint, method, payload)
            print(f"IP: {ip}, Endpoint: {endpoint}, Safe: {safe}, Threats: {len(threats)}")

            for threat in threats:
                print(f"  - {threat.threat_type.value}: {threat.description}")

        # Статистика
        stats = get_ids_statistics()
        print(f"\n📊 Statistics: {json.dumps(stats, indent=2)}")

        print("✅ Intrusion Detection System test completed")

    # Запуск тестов
    asyncio.run(test_ids())
