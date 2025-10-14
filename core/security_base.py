# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Base
Расширенный базовый класс безопасности для системы

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import hashlib
import secrets
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .base import ComponentStatus, SecurityBase


class ThreatType(Enum):
    """Типы угроз"""

    MALWARE = "malware"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    DATA_BREACH = "data_breach"
    NETWORK_ATTACK = "network_attack"
    INSIDER_THREAT = "insider_threat"
    ZERO_DAY = "zero_day"
    RANSOMWARE = "ransomware"


class IncidentSeverity(Enum):
    """Уровни серьезности инцидентов"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent:
    """Класс для представления события безопасности"""

    def __init__(
        self,
        event_type: str,
        severity: IncidentSeverity,
        description: str,
        source: str,
        timestamp: Optional[datetime] = None,
    ):
        self.event_type = event_type
        self.severity = severity
        self.description = description
        self.source = source
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.id = self._generate_event_id()
        self.resolved = False
        self.resolution_time = None

    def _generate_event_id(self) -> str:
        """Генерация уникального ID события"""
        data = f"{self.event_type}{self.source}{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _get_timestamp_str(self) -> Optional[str]:
        """Получение строки временной метки"""
        if self.timestamp is not None:
            return self.timestamp.isoformat()
        return None

    def _get_resolution_time_str(self) -> Optional[str]:
        """Получение строки времени разрешения"""
        if self.resolution_time is not None:
            return self.resolution_time.isoformat()
        return None

    def resolve(self):
        """Отметить событие как разрешенное"""
        self.resolved = True
        self.resolution_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity.value,
            "description": self.description,
            "source": self.source,
            "timestamp": self._get_timestamp_str(),
            "resolved": self.resolved,
            "resolution_time": self._get_resolution_time_str(),
        }


class SecurityRule:
    """Класс для представления правила безопасности"""

    def __init__(
        self,
        name: str,
        rule_type: str,
        conditions: Dict[str, Any],
        actions: List[str],
        enabled: bool = True,
    ):
        self.name = name
        self.rule_type = rule_type
        self.conditions = conditions
        self.actions = actions
        self.enabled = enabled
        self.created_at = datetime.now()
        self.last_triggered: Optional[datetime] = None
        self.trigger_count = 0

    def evaluate(self, event_data: Dict[str, Any]) -> bool:
        """
        Оценка правила на основе данных события

        Args:
            event_data: Данные события

        Returns:
            bool: True если правило сработало
        """
        if not self.enabled:
            return False

        try:
            # Простая логика оценки условий
            for condition_key, expected_value in self.conditions.items():
                if condition_key not in event_data:
                    return False

                actual_value = event_data[condition_key]
                if actual_value != expected_value:
                    return False

            self.last_triggered = datetime.now()
            self.trigger_count += 1
            return True

        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "name": self.name,
            "rule_type": self.rule_type,
            "conditions": self.conditions,
            "actions": self.actions,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_triggered": (
                self.last_triggered.isoformat()
                if self.last_triggered is not None else None
            ),
            "trigger_count": self.trigger_count,
        }


class AdvancedSecurityBase(SecurityBase):
    """Расширенный базовый класс безопасности"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.security_events: List[SecurityEvent] = []
        self.security_rules: List[Dict[str, Any]] = []
        self.threat_intelligence: Dict[str, Any] = {}
        self.incident_history: List[Dict[str, Any]] = []
        self.encryption_keys: Dict[str, Any] = {}
        self.access_control_list: Dict[str, Any] = {}
        self.audit_trail: List[Dict[str, Any]] = []

    def add_security_event(self, event: SecurityEvent) -> bool:
        """
        Добавление события безопасности

        Args:
            event: Событие безопасности

        Returns:
            bool: True если событие добавлено
        """
        try:
            self.security_events.append(event)
            self.audit_trail.append(
                {
                    "action": "security_event_added",
                    "event_id": event.id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Проверка правил безопасности
            self._evaluate_security_rules(event)

            self.log_activity(
                f"Добавлено событие безопасности: {event.event_type}")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка добавления события безопасности: {e}", "error")
            return False

    def add_security_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Добавление правила безопасности

        Args:
            rule: Правило безопасности

        Returns:
            bool: True если правило добавлено
        """
        try:
            self.security_rules.append(rule)
            self.audit_trail.append(
                {
                    "action": "security_rule_added",
                    "rule_name": rule.get("name", "Unknown"),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            self.log_activity(
                f"Добавлено правило безопасности: "
                f"{rule.get('name', 'Unknown')}"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка добавления правила безопасности: {e}", "error")
            return False

    def _evaluate_security_rules(self, event: SecurityEvent):
        """Оценка правил безопасности для события"""
        event_data = {
            "event_type": event.event_type,
            "severity": event.severity.value,
            "source": event.source,
        }

        for rule in self.security_rules:
            if self._evaluate_rule_dict(rule, event_data):
                self._execute_rule_actions_dict(rule, event)

    def _evaluate_rule_dict(
            self, rule: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Оценка правила безопасности в формате словаря"""
        try:
            if not rule.get("enabled", True):
                return False

            conditions = rule.get("conditions", {})
            for condition_key, expected_value in conditions.items():
                if condition_key not in event_data:
                    return False

                actual_value = event_data[condition_key]
                if actual_value != expected_value:
                    return False

            return True
        except Exception:
            return False

    def _execute_rule_actions_dict(
            self, rule: Dict[str, Any], event: SecurityEvent):
        """Выполнение действий правила в формате словаря"""
        actions = rule.get("actions", [])
        for action in actions:
            try:
                if action == "log":
                    self.log_activity(
                        f"Правило {rule.get('name', 'Unknown')} "
                        f"сработало для события {event.id}"
                    )
                elif action == "alert":
                    self._send_alert_dict(rule, event)
                elif action == "block":
                    self._block_source(event.source)
                elif action == "isolate":
                    self._isolate_system()
                else:
                    self.log_activity(
                        f"Неизвестное действие правила: {action}", "warning")
            except Exception as e:
                self.log_activity(
                    f"Ошибка выполнения действия {action}: {e}", "error")

    def _execute_rule_actions(self, rule: SecurityRule, event: SecurityEvent):
        """Выполнение действий правила"""
        for action in rule.actions:
            try:
                if action == "log":
                    self.log_activity(
                        f"Правило {rule.name} сработало для события "
                        f"{event.id}"
                    )
                elif action == "alert":
                    self._send_alert(rule, event)
                elif action == "block":
                    self._block_source(event.source)
                elif action == "isolate":
                    self._isolate_system()
                else:
                    self.log_activity(
                        f"Неизвестное действие правила: {action}", "warning")
            except Exception as e:
                self.log_activity(
                    f"Ошибка выполнения действия {action}: {e}", "error")

    def _send_alert_dict(self, rule: Dict[str, Any], event: SecurityEvent):
        """Отправка оповещения для правила в формате словаря"""
        alert_message = (
            f"Сработало правило {rule.get('name', 'Unknown')} "
            f"для события {event.id}"
        )
        self.log_activity(alert_message, "warning")

    def _send_alert(self, rule: SecurityRule, event: SecurityEvent):
        """Отправка оповещения"""
        alert_message = f"Сработало правило {rule.name} для события {event.id}"
        self.log_activity(alert_message, "warning")

    def _block_source(self, source: str):
        """Блокировка источника"""
        self.access_control_list[source] = {
            "blocked": True,
            "blocked_at": datetime.now(),
            "reason": "Security rule triggered",
        }
        self.log_activity(f"Заблокирован источник: {source}")

    def _isolate_system(self):
        """Изоляция системы"""
        self.log_activity("Система переведена в режим изоляции", "critical")

    def detect_threat(self, threat_info: Dict[str, Any]) -> bool:
        """
        Расширенное обнаружение угроз

        Args:
            threat_info: Информация об угрозе

        Returns:
            bool: True если угроза обработана
        """
        try:
            # Создание события безопасности
            threat_type = threat_info.get("type", "unknown")
            severity = self._determine_severity(threat_info)

            event = SecurityEvent(
                event_type=threat_type,
                severity=severity,
                description=threat_info.get("description", "Threat detected"),
                source=threat_info.get("source", "unknown"),
            )

            # Добавление события
            self.add_security_event(event)

            # Обновление статистики
            self.threats_detected += 1

            # Обработка угрозы
            success = self._handle_threat(threat_info)

            if success:
                self.incidents_handled += 1
                event.resolve()

            return success

        except Exception as e:
            self.log_activity(f"Ошибка обнаружения угрозы: {e}", "error")
            return False

    def _determine_severity(
            self, threat_info: Dict[str, Any]) -> IncidentSeverity:
        """Определение серьезности угрозы"""
        threat_type = threat_info.get("type", "unknown")

        # Логика определения серьезности
        if threat_type in ["ransomware", "zero_day"]:
            return IncidentSeverity.CRITICAL
        elif threat_type in ["data_breach", "network_attack"]:
            return IncidentSeverity.HIGH
        elif threat_type in ["phishing", "social_engineering"]:
            return IncidentSeverity.MEDIUM
        else:
            return IncidentSeverity.LOW

    def generate_encryption_key(
            self,
            key_name: str,
            key_size: int = 256) -> str:
        """
        Генерация ключа шифрования

        Args:
            key_name: Название ключа
            key_size: Размер ключа в битах

        Returns:
            str: Сгенерированный ключ
        """
        try:
            key = secrets.token_hex(key_size // 8)
            self.encryption_keys[key_name] = {
                "key": key,
                "created_at": datetime.now(),
                "size": key_size,
            }

            self.log_activity(f"Сгенерирован ключ шифрования: {key_name}")
            return key

        except Exception as e:
            self.log_activity(f"Ошибка генерации ключа: {e}", "error")
            return ""

    def get_encryption_key(self, key_name: str) -> Optional[str]:
        """
        Получение ключа шифрования

        Args:
            key_name: Название ключа

        Returns:
            Optional[str]: Ключ шифрования или None
        """
        key_info = self.encryption_keys.get(key_name)
        return key_info["key"] if key_info else None

    def encrypt_data(self, data: str, key_name: str) -> Tuple[bool, str]:
        """
        Шифрование данных

        Args:
            data: Данные для шифрования
            key_name: Название ключа

        Returns:
            Tuple[bool, str]: (успех, зашифрованные данные)
        """
        try:
            key = self.get_encryption_key(key_name)
            if not key:
                return False, ""

            # Простое XOR шифрование (для демонстрации)
            encrypted = ""
            for i, char in enumerate(data):
                key_char = key[i % len(key)]
                encrypted += chr(ord(char) ^ ord(key_char))

            return True, encrypted

        except Exception as e:
            self.log_activity(f"Ошибка шифрования: {e}", "error")
            return False, ""

    def decrypt_data(self, encrypted_data: str,
                     key_name: str) -> Tuple[bool, str]:
        """
        Расшифровка данных

        Args:
            encrypted_data: Зашифрованные данные
            key_name: Название ключа

        Returns:
            Tuple[bool, str]: (успех, расшифрованные данные)
        """
        try:
            key = self.get_encryption_key(key_name)
            if not key:
                return False, ""

            # Простое XOR расшифрование (для демонстрации)
            decrypted = ""
            for i, char in enumerate(encrypted_data):
                key_char = key[i % len(key)]
                decrypted += chr(ord(char) ^ ord(key_char))

            return True, decrypted

        except Exception as e:
            self.log_activity(f"Ошибка расшифровки: {e}", "error")
            return False, ""

    def get_security_report(self) -> Dict[str, Any]:
        """
        Расширенный отчет по безопасности

        Returns:
            Dict[str, Any]: Отчет по безопасности
        """
        base_report = super().get_security_report()

        # Дополнительная информация
        additional_info = {
            "security_events_count": len(
                self.security_events), "security_rules_count": len(
                self.security_rules
            ),
            "active_events": len([
                e for e in self.security_events if not e.resolved
            ]),
            "encryption_keys_count": len(self.encryption_keys),
            "blocked_sources_count": len([
                s for s in self.access_control_list.values()
                if s.get("blocked", False)
            ]),
            "audit_trail_entries": len(self.audit_trail),
            "threat_intelligence_sources": len(self.threat_intelligence),
        }

        base_report.update(additional_info)
        return base_report

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получение аудиторского следа

        Args:
            limit: Максимальное количество записей

        Returns:
            List[Dict[str, Any]]: Аудиторский след
        """
        return self.audit_trail[-limit:] if limit > 0 else self.audit_trail

    def clear_audit_trail(self):
        """Очистка аудиторского следа"""
        self.audit_trail.clear()
        self.log_activity("Аудиторский след очищен")

    def initialize(self) -> bool:
        """Расширенная инициализация компонента безопасности"""
        try:
            self.log_activity(
                f"Расширенная инициализация компонента безопасности "
                f"{self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Инициализация базовых правил безопасности
            self._initialize_security_rules()

            # Генерация базовых ключей шифрования
            self.generate_encryption_key("default", 256)
            self.generate_encryption_key("session", 128)

            # Инициализация угрозовой разведки
            self._initialize_threat_intelligence()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Компонент безопасности {self.name} успешно инициализирован")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации компонента безопасности "
                f"{self.name}: {e}",
                "error"
            )
            return False

    def _initialize_threat_intelligence(self):
        """Инициализация угрозовой разведки"""
        # Базовые источники угрозовой разведки
        self.threat_intelligence = {
            "malware_signatures": {},
            "phishing_patterns": [],
            "suspicious_ips": set(),
            "known_threats": {},
        }
        self.log_activity("Инициализирована угрозовая разведка")
