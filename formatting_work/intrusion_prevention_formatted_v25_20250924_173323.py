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
        try:
            # Валидация входных параметров
            if not log_entry or not isinstance(log_entry, str):
                print("⚠️ Предупреждение: Пустая или некорректная запись лога")
                return None

            if source_ip and not isinstance(source_ip, str):
                print("⚠️ Предупреждение: Некорректный IP адрес")
                source_ip = None

            self.total_attempts += 1

            # Проверяем по правилам
            for rule in self.rules.values():
                if not rule.is_active:
                    continue

                try:
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
                except re.error as e:
                    print(
                        f"❌ Ошибка в регулярном выражении правила "
                        f"{rule.rule_id}: {e}"
                    )
                    continue
                except Exception as e:
                    print(f"❌ Ошибка при анализе правила {rule.rule_id}: {e}")
                    continue

            return None

        except Exception as e:
            print(f"❌ Критическая ошибка в analyze_log_entry: {e}")
            return None

    def analyze_network_flow(
        self, flow: NetworkFlow
    ) -> Optional[IntrusionAttempt]:
        """Анализирует сетевой поток на наличие подозрительной активности"""
        try:
            # Валидация входных параметров
            if not flow or not isinstance(flow, NetworkFlow):
                print("⚠️ Предупреждение: Некорректный объект NetworkFlow")
                return None

            # Валидация полей NetworkFlow
            if not hasattr(flow, "source_ip") or not hasattr(flow, "dest_ip"):
                print("⚠️ Предупреждение: Неполный объект NetworkFlow")
                return None

            self.network_flows.append(flow)

            # Проверяем на DDoS
            try:
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
            except Exception as e:
                print(f"❌ Ошибка при проверке DDoS: {e}")

            # Проверяем на сканирование портов
            try:
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
            except Exception as e:
                print(f"❌ Ошибка при проверке сканирования портов: {e}")

            return None

        except Exception as e:
            print(f"❌ Критическая ошибка в analyze_network_flow: {e}")
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
        try:
            # Валидация входных параметров
            if not source_ip or not isinstance(source_ip, str):
                print("⚠️ Предупреждение: Некорректный IP адрес для rate limit")
                return False

            if not isinstance(max_attempts, int) or max_attempts <= 0:
                print(
                    "⚠️ Предупреждение: Некорректный max_attempts, "
                    "используется значение по умолчанию"
                )
                max_attempts = 10

            if not isinstance(window_seconds, int) or window_seconds <= 0:
                print(
                    "⚠️ Предупреждение: Некорректный window_seconds, "
                    "используется значение по умолчанию"
                )
                window_seconds = 60

            now = time.time()
            attempts = self.rate_limits[source_ip]

            # Удаляем старые попытки
            try:
                while attempts and now - attempts[0] > window_seconds:
                    attempts.popleft()
            except Exception as e:
                print(f"❌ Ошибка при очистке старых попыток: {e}")
                return False

            # Проверяем лимит
            if len(attempts) >= max_attempts:
                print(
                    f"⚠️ Превышен лимит попыток для {source_ip}: "
                    f"{len(attempts)}/{max_attempts}"
                )
                return False  # Превышен лимит

            # Добавляем текущую попытку
            try:
                attempts.append(now)
                return True
            except Exception as e:
                print(f"❌ Ошибка при добавлении попытки: {e}")
                return False

        except Exception as e:
            print(f"❌ Критическая ошибка в check_rate_limit: {e}")
            return False

    def is_ip_blocked(self, ip: str) -> bool:
        """Проверяет, заблокирован ли IP адрес"""
        try:
            # Валидация входных параметров
            if not ip or not isinstance(ip, str):
                print(
                    "⚠️ Предупреждение: Некорректный IP адрес для проверки блокировки"
                )
                return False

            # Проверяем, что IP не пустой и не содержит только пробелы
            ip = ip.strip()
            if not ip:
                print("⚠️ Предупреждение: Пустой IP адрес")
                return False

            return ip in self.blocked_ips

        except Exception as e:
            print(f"❌ Ошибка в is_ip_blocked: {e}")
            return False

    def is_ip_whitelisted(self, ip: str) -> bool:
        """Проверяет, находится ли IP в белом списке"""
        try:
            # Валидация входных параметров
            if not ip or not isinstance(ip, str):
                print(
                    "⚠️ Предупреждение: Некорректный IP адрес для проверки белого списка"
                )
                return False

            # Проверяем, что IP не пустой и не содержит только пробелы
            ip = ip.strip()
            if not ip:
                print("⚠️ Предупреждение: Пустой IP адрес")
                return False

            return ip in self.whitelist_ips

        except Exception as e:
            print(f"❌ Ошибка в is_ip_whitelisted: {e}")
            return False

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
        try:
            attack_types = defaultdict(int)
            threat_levels = defaultdict(int)

            # Безопасный подсчет попыток вторжения
            for attempt in self.intrusion_attempts:
                try:
                    if hasattr(attempt, "attack_type") and hasattr(
                        attempt.attack_type, "value"
                    ):
                        attack_types[attempt.attack_type.value] += 1
                    if hasattr(attempt, "threat_level") and hasattr(
                        attempt.threat_level, "value"
                    ):
                        threat_levels[attempt.threat_level.value] += 1
                except Exception as e:
                    print(f"❌ Ошибка при обработке попытки в статистике: {e}")
                    continue

            # Безопасный подсчет активных правил
            try:
                active_rules_count = len(
                    [
                        r
                        for r in self.rules.values()
                        if hasattr(r, "is_active") and r.is_active
                    ]
                )
            except Exception as e:
                print(f"❌ Ошибка при подсчете активных правил: {e}")
                active_rules_count = 0

            return {
                "total_attempts": getattr(self, "total_attempts", 0),
                "blocked_attempts": getattr(self, "blocked_attempts", 0),
                "alerted_attempts": getattr(self, "alerted_attempts", 0),
                "blocked_ips_count": len(getattr(self, "blocked_ips", set())),
                "whitelisted_ips_count": len(
                    getattr(self, "whitelist_ips", set())
                ),
                "active_rules_count": active_rules_count,
                "attack_types": dict(attack_types),
                "threat_levels": dict(threat_levels),
                "network_flows_count": len(getattr(self, "network_flows", [])),
            }

        except Exception as e:
            print(f"❌ Критическая ошибка в get_statistics: {e}")
            # Возвращаем базовую статистику в случае ошибки
            return {
                "total_attempts": 0,
                "blocked_attempts": 0,
                "alerted_attempts": 0,
                "blocked_ips_count": 0,
                "whitelisted_ips_count": 0,
                "active_rules_count": 0,
                "attack_types": {},
                "threat_levels": {},
                "network_flows_count": 0,
                "error": str(e),
            }

    def get_recent_attempts(self, hours: int = 24) -> List[IntrusionAttempt]:
        """Возвращает недавние попытки вторжения"""
        try:
            # Валидация входных параметров
            if not isinstance(hours, int) or hours < 0:
                print(
                    "⚠️ Предупреждение: Некорректное количество часов, используется значение по умолчанию"
                )
                hours = 24

            if hours > 8760:  # Максимум 1 год
                print(
                    "⚠️ Предупреждение: Слишком большое количество часов, ограничено до 8760 (1 год)"
                )
                hours = 8760

            cutoff_time = time.time() - (hours * 3600)

            # Фильтруем попытки с обработкой ошибок
            recent_attempts = []
            for attempt in self.intrusion_attempts:
                try:
                    if (
                        hasattr(attempt, "timestamp")
                        and attempt.timestamp > cutoff_time
                    ):
                        recent_attempts.append(attempt)
                except Exception as e:
                    print(f"❌ Ошибка при обработке попытки вторжения: {e}")
                    continue

            return recent_attempts

        except Exception as e:
            print(f"❌ Критическая ошибка в get_recent_attempts: {e}")
            return []

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
