# -*- coding: utf-8 -*-
"""
ALADDIN Security System - SecurityMonitoring
Мониторинг безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Добавляем путь к проекту
sys.path.append("/Users/sergejhlystov/ALADDIN_NEW")

from core.base import ComponentStatus, SecurityBase, SecurityLevel  # noqa: E402


class SecurityMonitoring(SecurityBase):
    """
    Мониторинг безопасности

    Критический компонент системы безопасности ALADDIN
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("SecurityMonitoring", config)
        self.name = "SecurityMonitoring"
        self.description = "Мониторинг безопасности"
        self.status = ComponentStatus.RUNNING
        self.security_level = SecurityLevel.CRITICAL
        self.config = config or {}

        # Данные мониторинга
        self.monitoring_data: Dict[str, Any] = {}

        # Инициализация компонента
        self._initialize_component()

        self.log_activity(f"{self.name} инициализирован", "info")

    def _initialize_component(self):
        """Инициализация компонента"""
        try:
            # Настройка логирования
            self.logger = logging.getLogger(f"aladdin.{self.name.lower()}")

            # Инициализация специфичных для компонента параметров
            self._setup_component_specific_config()

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации {self.name}: {e}", "error"
            )
            raise

    def _setup_component_specific_config(self):
        """Настройка специфичной конфигурации компонента"""
        # Переопределить в наследниках
        pass

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение основной функции компонента

        Args:
            params: Параметры выполнения

        Returns:
            Dict с результатами выполнения
        """
        try:
            self.log_activity(
                f"Выполнение {self.name} с параметрами: {params}", "info"
            )

            # Основная логика компонента
            result = self._execute_component_logic(params)

            self.log_activity(f"{self.name} выполнен успешно", "info")
            return {
                "success": True,
                "result": result,
                "component": self.name,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.log_activity(f"Ошибка выполнения {self.name}: {e}", "error")
            return {
                "success": False,
                "error": str(e),
                "component": self.name,
                "timestamp": datetime.now().isoformat(),
            }

    def _execute_component_logic(self, params: Dict[str, Any]) -> Any:
        """
        Основная логика компонента
        Переопределить в наследниках
        """
        return {"message": f"{self.name} выполнен", "params": params}

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса компонента

        Returns:
            Dict с информацией о статусе
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "security_level": self.security_level.value,
            "active": self.status == ComponentStatus.RUNNING,
            "timestamp": datetime.now().isoformat(),
        }

    def enable(self) -> bool:
        """Включение компонента"""
        try:
            self.status = ComponentStatus.RUNNING
            self.log_activity(f"{self.name} включен", "info")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка включения {self.name}: {e}", "error")
            return False

    def disable(self) -> bool:
        """Отключение компонента"""
        try:
            self.status = ComponentStatus.INACTIVE
            self.log_activity(f"{self.name} отключен", "info")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка отключения {self.name}: {e}", "error")
            return False

    # ============================================================================
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ СОВМЕСТИМОСТИ С SFM
    # ============================================================================

    def add_monitoring_rule(self, rule) -> None:
        """Добавление правила мониторинга (совместимость с SFM)"""
        try:
            if hasattr(rule, "rule_id"):
                rule_id = rule.rule_id
            else:
                rule_id = f"rule_{len(self.security_rules) + 1}"

            self.security_rules[rule_id] = rule
            self.log_activity(f"Добавлено правило мониторинга: {rule_id}")
        except Exception as e:
            self.log_activity(
                f"Ошибка добавления правила мониторинга: {e}", "error"
            )

    def add_alert(self, alert: Dict[str, Any]) -> None:
        """Добавление алерта (совместимость с SFM)"""
        try:
            alert_id = alert.get(
                "type", f"alert_{len(self.security_events) + 1}"
            )
            self.add_security_event(
                alert_id,
                alert.get("message", ""),
                alert.get("severity", "medium"),
            )
        except Exception as e:
            self.log_activity(f"Ошибка добавления алерта: {e}", "error")

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Получение статистики мониторинга (совместимость с SFM)"""
        return {
            "total_events": len(self.security_events),
            "total_rules": len(self.security_rules),
            "threats_detected": self.threats_detected,
            "incidents_handled": self.incidents_handled,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
            "status": (
                self.status.value
                if hasattr(self.status, "value")
                else str(self.status)
            ),
        }

    @property
    def alert_retention_days(self) -> int:
        """Количество дней хранения алертов"""
        return getattr(self, "_alert_retention_days", 30)

    @alert_retention_days.setter
    def alert_retention_days(self, value: int) -> None:
        """Установка количества дней хранения алертов"""
        self._alert_retention_days = value
