"""
Модуль No-Logs политики для ALADDIN VPN
Обеспечивает отсутствие логирования персональных данных и трафика пользователей
"""

import json

# Настройка логирования
import logging as std_logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class LogType(Enum):
    """Типы логов"""

    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    PERSONAL_DATA = "personal_data"  # НЕ ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ
    TRAFFIC = "traffic"  # НЕ ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ
    USER_ACTIVITY = "user_activity"  # НЕ ДОЛЖЕН ИСПОЛЬЗОВАТЬСЯ


class LogLevel(Enum):
    """Уровни логов"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Запись лога"""

    timestamp: datetime
    level: LogLevel
    log_type: LogType
    message: str
    data: Optional[Dict[str, Any]] = None
    is_anonymized: bool = True


class NoLogsPolicyManager:
    """Менеджер No-Logs политики"""

    def __init__(self):
        self.forbidden_log_types = {
            LogType.PERSONAL_DATA,
            LogType.TRAFFIC,
            LogType.USER_ACTIVITY,
        }
        self.allowed_log_types = {
            LogType.SYSTEM,
            LogType.SECURITY,
            LogType.PERFORMANCE,
        }
        self.log_entries: List[LogEntry] = []
        self.policy_violations: List[Dict[str, Any]] = []

    def log_system_event(
        self,
        level: LogLevel,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Логирование системного события"""
        return self._log_event(LogType.SYSTEM, level, message, data)

    def log_security_event(
        self,
        level: LogLevel,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Логирование события безопасности"""
        return self._log_event(LogType.SECURITY, level, message, data)

    def log_performance_event(
        self,
        level: LogLevel,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Логирование события производительности"""
        return self._log_event(LogType.PERFORMANCE, level, message, data)

    def _log_event(
        self,
        log_type: LogType,
        level: LogLevel,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Внутренний метод логирования"""
        try:
            # Проверяем, что тип лога разрешен
            if log_type in self.forbidden_log_types:
                self._record_policy_violation(log_type, message, data)
                return False

            # Обезличиваем данные если необходимо
            anonymized_data = self._anonymize_data(data) if data else None

            # Создаем запись лога
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=level,
                log_type=log_type,
                message=message,
                data=anonymized_data,
                is_anonymized=True,
            )

            # Добавляем в список логов
            self.log_entries.append(log_entry)

            # В реальной реализации здесь будет запись в файл или БД
            logger.info(f"[{log_type.value}] {message}")

            return True

        except Exception as e:
            logger.error(f"Ошибка логирования: {e}")
            return False

    def _anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обезличивание данных"""
        if not data:
            return data

        anonymized_data = {}

        for key, value in data.items():
            # Список полей, которые нужно обезличить
            personal_fields = {
                "user_id",
                "username",
                "email",
                "phone",
                "ip_address",
                "mac_address",
                "device_id",
                "session_id",
                "user_agent",
                "referer",
                "url",
                "domain",
                "query",
                "path",
            }

            if key.lower() in personal_fields:
                # Обезличиваем персональные поля
                anonymized_data[key] = self._hash_value(str(value))
            elif isinstance(value, dict):
                # Рекурсивно обезличиваем вложенные словари
                anonymized_data[key] = self._anonymize_data(value)
            elif isinstance(value, list):
                # Обезличиваем списки
                anonymized_data[key] = [
                    (
                        self._anonymize_data(item)
                        if isinstance(item, dict)
                        else self._hash_value(str(item))
                    )
                    for item in value
                ]
            else:
                # Оставляем как есть
                anonymized_data[key] = value

        return anonymized_data

    def _hash_value(self, value: str) -> str:
        """Хеширование значения для обезличивания"""
        import hashlib

        return hashlib.sha256(value.encode()).hexdigest()[:8]

    def _record_policy_violation(
        self,
        log_type: LogType,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        """Запись нарушения политики No-Logs"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "log_type": log_type.value,
            "message": message,
            "data": data,
            "severity": "HIGH",
        }

        self.policy_violations.append(violation)
        logger.error(
            f"НАРУШЕНИЕ NO-LOGS ПОЛИТИКИ: {log_type.value} - {message}"
        )

    def check_no_logs_compliance(self) -> Dict[str, Any]:
        """Проверка соответствия No-Logs политике"""
        logger.info("Проверка соответствия No-Logs политике")

        # Проверяем нарушения политики
        violations_count = len(self.policy_violations)

        # Проверяем типы логов
        forbidden_logs = [
            log
            for log in self.log_entries
            if log.log_type in self.forbidden_log_types
        ]
        forbidden_logs_count = len(forbidden_logs)

        # Проверяем обезличивание данных
        non_anonymized_logs = [
            log for log in self.log_entries if not log.is_anonymized
        ]
        non_anonymized_count = len(non_anonymized_logs)

        # Общий статус соответствия
        is_compliant = (
            violations_count == 0
            and forbidden_logs_count == 0
            and non_anonymized_count == 0
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "is_compliant": is_compliant,
            "total_logs": len(self.log_entries),
            "violations_count": violations_count,
            "forbidden_logs_count": forbidden_logs_count,
            "non_anonymized_count": non_anonymized_count,
            "compliance_percentage": self._calculate_compliance_percentage(
                violations_count, forbidden_logs_count, non_anonymized_count
            ),
            "violations": self.policy_violations,
            "forbidden_logs": [
                self._log_to_dict(log) for log in forbidden_logs
            ],
            "non_anonymized_logs": [
                self._log_to_dict(log) for log in non_anonymized_logs
            ],
        }

        logger.info(
            f"No-Logs политика: {'✅ СООТВЕТСТВУЕТ' if is_compliant else '❌ НЕ СООТВЕТСТВУЕТ'}"
        )
        return result

    def _calculate_compliance_percentage(
        self, violations: int, forbidden_logs: int, non_anonymized: int
    ) -> float:
        """Расчет процента соответствия No-Logs политике"""
        total_issues = violations + forbidden_logs + non_anonymized
        if total_issues == 0:
            return 100.0

        # Штрафуем за каждое нарушение
        penalty_per_violation = 20.0
        penalty_per_forbidden = 30.0
        penalty_per_non_anonymized = 25.0

        total_penalty = (
            violations * penalty_per_violation
            + forbidden_logs * penalty_per_forbidden
            + non_anonymized * penalty_per_non_anonymized
        )

        compliance = max(0.0, 100.0 - total_penalty)
        return compliance

    def _log_to_dict(self, log: LogEntry) -> Dict[str, Any]:
        """Преобразование лога в словарь"""
        return {
            "timestamp": log.timestamp.isoformat(),
            "level": log.level.value,
            "log_type": log.log_type.value,
            "message": log.message,
            "data": log.data,
            "is_anonymized": log.is_anonymized,
        }

    def get_log_statistics(self) -> Dict[str, Any]:
        """Получение статистики логов"""
        if not self.log_entries:
            return {"message": "Логи отсутствуют"}

        # Группируем по типам
        log_types = {}
        for log in self.log_entries:
            log_type = log.log_type.value
            if log_type not in log_types:
                log_types[log_type] = 0
            log_types[log_type] += 1

        # Группируем по уровням
        log_levels = {}
        for log in self.log_entries:
            level = log.level.value
            if level not in log_levels:
                log_levels[level] = 0
            log_levels[level] += 1

        return {
            "total_logs": len(self.log_entries),
            "log_types": log_types,
            "log_levels": log_levels,
            "anonymized_logs": len(
                [log for log in self.log_entries if log.is_anonymized]
            ),
            "non_anonymized_logs": len(
                [log for log in self.log_entries if not log.is_anonymized]
            ),
        }

    def clear_logs(self) -> bool:
        """Очистка логов"""
        try:
            self.log_entries.clear()
            self.policy_violations.clear()
            logger.info("Логи очищены")
            return True
        except Exception as e:
            logger.error(f"Ошибка очистки логов: {e}")
            return False

    def export_compliance_report(self) -> Dict[str, Any]:
        """Экспорт отчета о соответствии"""
        compliance_result = self.check_no_logs_compliance()
        statistics = self.get_log_statistics()

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "compliance": compliance_result,
            "statistics": statistics,
            "recommendations": self._get_recommendations(compliance_result),
        }

        return report

    def _get_recommendations(
        self, compliance_result: Dict[str, Any]
    ) -> List[str]:
        """Получение рекомендаций по улучшению"""
        recommendations = []

        if compliance_result["violations_count"] > 0:
            recommendations.append("Устранить нарушения No-Logs политики")

        if compliance_result["forbidden_logs_count"] > 0:
            recommendations.append("Удалить логи запрещенных типов")

        if compliance_result["non_anonymized_count"] > 0:
            recommendations.append("Обезличить все логи")

        if not recommendations:
            recommendations.append("No-Logs политика соблюдается корректно")

        return recommendations


# Пример использования
if __name__ == "__main__":
    no_logs_manager = NoLogsPolicyManager()

    # Логируем разрешенные события
    no_logs_manager.log_system_event(LogLevel.INFO, "Система запущена")
    no_logs_manager.log_security_event(
        LogLevel.WARNING, "Обнаружена подозрительная активность"
    )
    no_logs_manager.log_performance_event(
        LogLevel.INFO, "Производительность в норме"
    )

    # Проверяем соответствие
    result = no_logs_manager.check_no_logs_compliance()

    print("=== ПРОВЕРКА NO-LOGS ПОЛИТИКИ ===")
    print(f"Соответствие: {result['compliance_percentage']:.1f}%")
    print(
        f"Статус: {'✅ СООТВЕТСТВУЕТ' if result['is_compliant'] else '❌ НЕ СООТВЕТСТВУЕТ'}"
    )
    print(f"Всего логов: {result['total_logs']}")
    print(f"Нарушений: {result['violations_count']}")
    print(f"Запрещенных логов: {result['forbidden_logs_count']}")
    print(f"Необезличенных логов: {result['non_anonymized_count']}")

    # Получаем статистику
    stats = no_logs_manager.get_log_statistics()
    print("\n=== СТАТИСТИКА ЛОГОВ ===")
    print(f"Типы логов: {stats['log_types']}")
    print(f"Уровни логов: {stats['log_levels']}")
    print(f"Обезличенных: {stats['anonymized_logs']}")
    print(f"Необезличенных: {stats['non_anonymized_logs']}")
