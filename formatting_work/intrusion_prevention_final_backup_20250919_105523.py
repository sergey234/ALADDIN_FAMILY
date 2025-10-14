# -*- coding: utf-8 -*-
"""
ALADDIN Security System - IntrusionPrevention
Предотвращение вторжений - КРИТИЧНО

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import json
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ThreatLevel(Enum):
    """Уровни угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(Enum):
    """Типы атак"""

    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    PORT_SCAN = "port_scan"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    MALWARE = "malware"
    PHISHING = "phishing"
    MAN_IN_THE_MIDDLE = "mitm"
    ZERO_DAY = "zero_day"


class ActionType(Enum):
    """Типы действий"""

    ALLOW = "allow"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ALERT = "alert"
    LOG = "log"


@dataclass
class IntrusionAttempt:
    """Попытка вторжения"""

    source_ip: str
    target_ip: str
    port: int
    attack_type: AttackType
    threat_level: ThreatLevel
    timestamp: float
    payload: str
    user_agent: str
    session_id: str
    is_blocked: bool = False
    action_taken: ActionType = ActionType.LOG


@dataclass
class SecurityRule:
    """Правило безопасности"""

    rule_id: str
    name: str
    description: str
    pattern: str
    attack_type: AttackType
    threat_level: ThreatLevel
    action: ActionType
    is_active: bool = True
    created_at: float = 0.0
    updated_at: float = 0.0


@dataclass
class NetworkFlow:
    """Сетевой поток"""

    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    start_time: float
    end_time: float
    duration: float


class IntrusionPrevention:
    """Система предотвращения вторжений"""

    def __init__(self):
        self.rules: Dict[str, SecurityRule] = {}
        self.intrusion_attempts: List[IntrusionAttempt] = []
        self.blocked_ips: set = set()
        self.whitelist_ips: set = set()
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque())
        self.network_flows: List[NetworkFlow] = []
        self.is_active = True
        self.alert_threshold = 10  # Количество попыток для алерта
        self.block_threshold = 50  # Количество попыток для блокировки

        # Статистика
        self.total_attempts = 0
        self.blocked_attempts = 0
        self.alerted_attempts = 0

        # Загружаем базовые правила
        self._load_default_rules()

    def _load_default_rules(self):
        """Загружает базовые правила безопасности"""
        default_rules = [
            {
                "rule_id": "brute_force_ssh",
                "name": "SSH Brute Force Protection",
                "description": "Защита от атак перебора SSH",
                "pattern": r"Failed password for.*from.*port.*ssh2",
                "attack_type": AttackType.BRUTE_FORCE,
                "threat_level": ThreatLevel.HIGH,
                "action": ActionType.BLOCK,
            },
            {
                "rule_id": "sql_injection",
                "name": "SQL Injection Protection",
                "description": "Защита от SQL инъекций",
                "pattern": (
                    r"(union|select|insert|update|delete|drop|"
                    r"create|alter).*from"
                ),
                "attack_type": AttackType.SQL_INJECTION,
                "threat_level": ThreatLevel.CRITICAL,
                "action": ActionType.BLOCK,
            },
            {
                "rule_id": "xss_attack",
                "name": "XSS Protection",
                "description": "Защита от XSS атак",
                "pattern": r"<script.*>.*</script>|<img.*onerror|<iframe.*src",
                "attack_type": AttackType.XSS,
                "threat_level": ThreatLevel.HIGH,
                "action": ActionType.BLOCK,
            },
            {
                "rule_id": "port_scan",
                "name": "Port Scan Detection",
                "description": "Обнаружение сканирования портов",
                "pattern": r"Connection.*refused|No route to host",
                "attack_type": AttackType.PORT_SCAN,
                "threat_level": ThreatLevel.MEDIUM,
                "action": ActionType.ALERT,
            },
            {
                "rule_id": "ddos_attack",
                "name": "DDoS Protection",
                "description": "Защита от DDoS атак",
                "pattern": r"Too many connections|Connection limit exceeded",
                "attack_type": AttackType.DDoS,
                "threat_level": ThreatLevel.CRITICAL,
                "action": ActionType.BLOCK,
            },
        ]

        for rule_data in default_rules:
            rule = SecurityRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                pattern=rule_data["pattern"],
                attack_type=rule_data["attack_type"],
                threat_level=rule_data["threat_level"],
                action=rule_data["action"],
                created_at=time.time(),
                updated_at=time.time(),
            )
            self.rules[rule.rule_id] = rule

    def add_rule(self, rule: SecurityRule):
        """Добавляет новое правило безопасности"""
        rule.created_at = time.time()
        rule.updated_at = time.time()
        self.rules[rule.rule_id] = rule
        print(f"✅ Добавлено правило: {rule.name}")

    def remove_rule(self, rule_id: str) -> bool:
        """Удаляет правило безопасности"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            print(f"🗑️ Удалено правило: {rule_id}")
            return True
        return False

    def update_rule(self, rule_id: str, **kwargs) -> bool:
        """Обновляет правило безопасности"""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            rule.updated_at = time.time()
            print(f"🔄 Обновлено правило: {rule_id}")
            return True
        return False

    def analyze_log_entry(
        self, log_entry: str, source_ip: str = None
    ) -> Optional[IntrusionAttempt]:
        """Анализирует запись лога на наличие попыток вторжения"""
        self.total_attempts += 1

        # Проверяем по правилам
        for rule in self.rules.values():
            if not rule.is_active:
                continue

            if re.search(rule.pattern, log_entry, re.IGNORECASE):
                attempt = IntrusionAttempt(
                    source_ip=source_ip or "unknown",
                    target_ip="localhost",
                    port=0,
                    attack_type=rule.attack_type,
                    threat_level=rule.threat_level,
                    timestamp=time.time(),
                    payload=log_entry[:200],  # Первые 200 символов
                    user_agent="unknown",
                    session_id="unknown",
                )

                # Применяем действие
                self._apply_action(attempt, rule.action)

                self.intrusion_attempts.append(attempt)
                return attempt

        return None

    def analyze_network_flow(
        self, flow: NetworkFlow
    ) -> Optional[IntrusionAttempt]:
        """Анализирует сетевой поток на наличие подозрительной активности"""
        self.network_flows.append(flow)

        # Проверяем на DDoS
        if self._is_ddos_attack(flow):
            attempt = IntrusionAttempt(
                source_ip=flow.source_ip,
                target_ip=flow.dest_ip,
                port=flow.dest_port,
                attack_type=AttackType.DDoS,
                threat_level=ThreatLevel.CRITICAL,
                timestamp=time.time(),
                payload=f"High packet rate: {flow.packets_sent} packets/sec",
                user_agent="unknown",
                session_id="unknown",
            )

            self._apply_action(attempt, ActionType.BLOCK)
            self.intrusion_attempts.append(attempt)
            return attempt

        # Проверяем на сканирование портов
        if self._is_port_scan(flow):
            attempt = IntrusionAttempt(
                source_ip=flow.source_ip,
                target_ip=flow.dest_ip,
                port=flow.dest_port,
                attack_type=AttackType.PORT_SCAN,
                threat_level=ThreatLevel.MEDIUM,
                timestamp=time.time(),
                payload=f"Port scan detected on port {flow.dest_port}",
                user_agent="unknown",
                session_id="unknown",
            )

            self._apply_action(attempt, ActionType.ALERT)
            self.intrusion_attempts.append(attempt)
            return attempt

        return None

    def _is_ddos_attack(self, flow: NetworkFlow) -> bool:
        """Проверяет, является ли поток DDoS атакой"""
        # Простая эвристика: много пакетов за короткое время
        if flow.duration > 0:
            packet_rate = flow.packets_sent / flow.duration
            return packet_rate > 1000  # Более 1000 пакетов в секунду
        return False

    def _is_port_scan(self, flow: NetworkFlow) -> bool:
        """Проверяет, является ли поток сканированием портов"""
        # Простая эвристика: много соединений на разные порты
        source_flows = [
            f for f in self.network_flows if f.source_ip == flow.source_ip
        ]
        unique_ports = len(set(f.dest_port for f in source_flows))
        return unique_ports > 10  # Более 10 разных портов

    def _apply_action(self, attempt: IntrusionAttempt, action: ActionType):
        """Применяет действие к попытке вторжения"""
        attempt.action_taken = action

        if action == ActionType.BLOCK:
            self.blocked_ips.add(attempt.source_ip)
            attempt.is_blocked = True
            self.blocked_attempts += 1
            print(f"🚫 ЗАБЛОКИРОВАН IP: {attempt.source_ip}")

        elif action == ActionType.ALERT:
            self.alerted_attempts += 1
            print(
                f"🚨 АЛЕРТ: {attempt.attack_type.value} от {attempt.source_ip}"
            )

        elif action == ActionType.QUARANTINE:
            # Здесь можно добавить логику карантина
            print(f"🔒 КАРАНТИН: {attempt.source_ip}")

    def check_rate_limit(
        self, source_ip: str, max_attempts: int = 10, window_seconds: int = 60
    ) -> bool:
        """Проверяет лимит попыток для IP адреса"""
        now = time.time()
        attempts = self.rate_limits[source_ip]

        # Удаляем старые попытки
        while attempts and now - attempts[0] > window_seconds:
            attempts.popleft()

        # Проверяем лимит
        if len(attempts) >= max_attempts:
            return False  # Превышен лимит

        # Добавляем текущую попытку
        attempts.append(now)
        return True

    def is_ip_blocked(self, ip: str) -> bool:
        """Проверяет, заблокирован ли IP адрес"""
        return ip in self.blocked_ips

    def is_ip_whitelisted(self, ip: str) -> bool:
        """Проверяет, находится ли IP в белом списке"""
        return ip in self.whitelist_ips

    def add_to_whitelist(self, ip: str):
        """Добавляет IP в белый список"""
        self.whitelist_ips.add(ip)
        print(f"✅ IP добавлен в белый список: {ip}")

    def remove_from_whitelist(self, ip: str):
        """Удаляет IP из белого списка"""
        self.whitelist_ips.discard(ip)
        print(f"🗑️ IP удален из белого списка: {ip}")

    def unblock_ip(self, ip: str):
        """Разблокирует IP адрес"""
        self.blocked_ips.discard(ip)
        print(f"🔓 IP разблокирован: {ip}")

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику системы"""
        attack_types = defaultdict(int)
        threat_levels = defaultdict(int)

        for attempt in self.intrusion_attempts:
            attack_types[attempt.attack_type.value] += 1
            threat_levels[attempt.threat_level.value] += 1

        return {
            "total_attempts": self.total_attempts,
            "blocked_attempts": self.blocked_attempts,
            "alerted_attempts": self.alerted_attempts,
            "blocked_ips_count": len(self.blocked_ips),
            "whitelisted_ips_count": len(self.whitelist_ips),
            "active_rules_count": len(
                [r for r in self.rules.values() if r.is_active]
            ),
            "attack_types": dict(attack_types),
            "threat_levels": dict(threat_levels),
            "network_flows_count": len(self.network_flows),
        }

    def get_recent_attempts(self, hours: int = 24) -> List[IntrusionAttempt]:
        """Возвращает недавние попытки вторжения"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            attempt
            for attempt in self.intrusion_attempts
            if attempt.timestamp > cutoff_time
        ]

    def export_rules(self, filename: str) -> bool:
        """Экспортирует правила в файл"""
        try:
            rules_data = []
            for rule in self.rules.values():
                rules_data.append(
                    {
                        "rule_id": rule.rule_id,
                        "name": rule.name,
                        "description": rule.description,
                        "pattern": rule.pattern,
                        "attack_type": rule.attack_type.value,
                        "threat_level": rule.threat_level.value,
                        "action": rule.action.value,
                        "is_active": rule.is_active,
                        "created_at": rule.created_at,
                        "updated_at": rule.updated_at,
                    }
                )

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Правила экспортированы в {filename}")
            return True

        except Exception as e:
            print(f"❌ Ошибка экспорта правил: {e}")
            return False

    def import_rules(self, filename: str) -> bool:
        """Импортирует правила из файла"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                rules_data = json.load(f)

            imported_count = 0
            for rule_data in rules_data:
                rule = SecurityRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    pattern=rule_data["pattern"],
                    attack_type=AttackType(rule_data["attack_type"]),
                    threat_level=ThreatLevel(rule_data["threat_level"]),
                    action=ActionType(rule_data["action"]),
                    is_active=rule_data["is_active"],
                    created_at=rule_data.get("created_at", time.time()),
                    updated_at=rule_data.get("updated_at", time.time()),
                )
                self.rules[rule.rule_id] = rule
                imported_count += 1

            print(f"✅ Импортировано {imported_count} правил из {filename}")
            return True

        except Exception as e:
            print(f"❌ Ошибка импорта правил: {e}")
            return False


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр системы предотвращения вторжений
    ips = IntrusionPrevention()

    # Тестируем с примером лога
    test_log = "Failed password for root from 192.168.1.100 port 22 ssh2"
    attempt = ips.analyze_log_entry(test_log, "192.168.1.100")

    if attempt:
        print(f"🚨 Обнаружена попытка вторжения: {attempt.attack_type.value}")
        print(f"   IP: {attempt.source_ip}")
        print(f"   Уровень угрозы: {attempt.threat_level.value}")
        print(f"   Действие: {attempt.action_taken.value}")

    # Выводим статистику
    stats = ips.get_statistics()
    print("\n📊 СТАТИСТИКА IPS:")
    print(f"   Всего попыток: {stats['total_attempts']}")
    print(f"   Заблокировано: {stats['blocked_attempts']}")
    print(f"   Алертов: {stats['alerted_attempts']}")
    print(f"   Заблокированных IP: {stats['blocked_ips_count']}")
    print(f"   Активных правил: {stats['active_rules_count']}")
