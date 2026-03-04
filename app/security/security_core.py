# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Core
Основной модуль безопасности для Фазы 2

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .access_control import AccessControl
from .audit_system import AuditSystem
from .authentication import AuthenticationManager
from .compliance_manager import ComplianceManager
from .incident_response import IncidentResponseManager
from .safe_function_manager import SafeFunctionManager
from .security_analytics import SecurityAnalyticsManager
from .security_audit import SecurityAuditManager
from .security_layer import SecurityLayer
from .security_monitoring import SecurityMonitoringManager
from .security_policy import SecurityPolicyManager
from .security_reporting import SecurityReportingManager
from .threat_intelligence import ThreatIntelligenceManager


class SecurityCore:
    """Основной модуль безопасности ALADDIN"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.components = {}
        self.status = "initializing"
        self.start_time = None

        # Инициализация компонентов
        self._initialize_components()

    def _initialize_components(self):
        """Инициализация всех компонентов безопасности"""
        try:
            # Базовые компоненты
            self.components["security_layer"] = SecurityLayer()
            self.components["audit_system"] = AuditSystem()
            self.components["access_control"] = AccessControl()
            self.components["safe_function_manager"] = SafeFunctionManager()
            self.components["authentication"] = AuthenticationManager()

            # Расширенные компоненты
            self.components["threat_intelligence"] = ThreatIntelligenceManager()
            self.components["incident_response"] = IncidentResponseManager()
            self.components["compliance_manager"] = ComplianceManager()
            self.components["security_analytics"] = SecurityAnalyticsManager()
            self.components["security_monitoring"] = SecurityMonitoringManager()
            self.components["security_reporting"] = SecurityReportingManager()
            self.components["security_audit"] = SecurityAuditManager()
            self.components["security_policy"] = SecurityPolicyManager()

            self.status = "initialized"
            print("✅ SecurityCore: Все компоненты инициализированы")

        except Exception as e:
            self.status = "error"
            print(f"❌ SecurityCore: Ошибка инициализации: {str(e)}")

    def start(self) -> bool:
        """Запуск всех компонентов безопасности"""
        try:
            self.status = "starting"
            self.start_time = datetime.now()

            for name, component in self.components.items():
                if hasattr(component, "start"):
                    component.start()
                    print(f"✅ {name}: Запущен")

            self.status = "running"
            print("✅ SecurityCore: Все компоненты запущены")
            return True

        except Exception as e:
            self.status = "error"
            print(f"❌ SecurityCore: Ошибка запуска: {str(e)}")
            return False

    def stop(self) -> bool:
        """Остановка всех компонентов безопасности"""
        try:
            self.status = "stopping"

            for name, component in self.components.items():
                if hasattr(component, "stop"):
                    component.stop()
                    print(f"✅ {name}: Остановлен")

            self.status = "stopped"
            print("✅ SecurityCore: Все компоненты остановлены")
            return True

        except Exception as e:
            self.status = "error"
            print(f"❌ SecurityCore: Ошибка остановки: {str(e)}")
            return False

    def get_component(self, name: str) -> Optional[Any]:
        """Получение компонента по имени"""
        return self.components.get(name)

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса всех компонентов"""
        status = {
            "core_status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "components": {},
        }

        for name, component in self.components.items():
            if hasattr(component, "status"):
                status["components"][name] = component.status
            else:
                status["components"][name] = "unknown"

        return status

    def run_security_check(self) -> Dict[str, Any]:
        """Запуск комплексной проверки безопасности"""
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unknown",
                "components": {},
                "issues": [],
                "recommendations": [],
            }

            # Проверяем каждый компонент
            for name, component in self.components.items():
                component_status = "unknown"
                if hasattr(component, "status"):
                    component_status = component.status

                results["components"][name] = component_status

                # Проверяем критические проблемы
                if component_status == "error":
                    results["issues"].append(f"Критическая ошибка в {name}")
                    results["recommendations"].append(f"Перезапустить компонент {name}")

            # Определяем общий статус
            if any(status == "error" for status in results["components"].values()):
                results["overall_status"] = "critical"
            elif all(status in ["running", "initialized"] for status in results["components"].values()):
                results["overall_status"] = "healthy"
            else:
                results["overall_status"] = "degraded"

            return results

        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e),
            }


# Создаем глобальный экземпляр
SECURITY_CORE = SecurityCore()
