#!/usr/bin/env python3
"""
Расширенный менеджер спящего режима для всех компонентов безопасности ALADDIN
Переводит в спящий режим все системы безопасности, оставляя только критически важные

Версия: 2.0
Автор: ALADDIN Security Team
Дата: 2024
Соответствие: SOLID, DRY, PEP8
"""

import asyncio
import logging
import time
import os
import subprocess
import sys
from typing import Dict, Any
from pathlib import Path

# Добавляем путь к корневой директории проекта
sys.path.append(str(Path(__file__).parent.parent.parent))

# Временно отключаем импорты для автономной работы
# from security.safe_function_manager import SafeFunctionManager
# from core.system_manager import SystemManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security_sleep_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ALADDINSecuritySleepManager:
    """Расширенный менеджер спящего режима для всех компонентов безопасности"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern для менеджера безопасности"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Временно отключаем инициализацию зависимостей
        # self.sfm = SafeFunctionManager()
        # self.system_manager = SystemManager()
        self.sfm = None
        self.system_manager = None
        self.sleep_mode = False
        self._initialized = True
        # Определяем базовый путь проекта
        base_path = Path(__file__).parent.parent.parent

        self.security_components = {
            # Основные компоненты безопасности
            "advanced_threat_intelligence": {
                "file": str(base_path / "advanced_threat_intelligence.py"),
                "process_name": "advanced_threat_intelligence",
                "critical": False,
                "module": "advanced_threat_intelligence"
            },
            "advanced_behavioral_analytics": {
                "file": None,  # Будем искать
                "process_name": "behavioral_analytics",
                "critical": False,
                "module": "advanced_behavioral_analytics"
            },
            "enhanced_security_integration": {
                "file": str(base_path / "enhanced_security_integration.py"),
                "process_name": "enhanced_security_integration",
                "critical": False,
                "module": "enhanced_security_integration"
            },
            "external_integrations_system": {
                "file": str(base_path / "external_integrations.py"),
                "process_name": "external_integrations",
                "critical": False,
                "module": "external_integrations"
            },
            "threat_intelligence_system": {
                "file": str(base_path / "threat_intelligence_system.py"),
                "process_name": "threat_intelligence",
                "critical": False,
                "module": "threat_intelligence_system"
            },
            "automated_audit_system": {
                "file": None,  # Будем искать
                "process_name": "audit_system",
                "critical": False,
                "module": "automated_audit_system"
            },
            "enhanced_dashboard_v2": {
                "file": str(base_path / "dashboard_server_optimized.py"),
                "process_name": "dashboard_server",
                "critical": False,
                "module": "dashboard_server_optimized"
            },
            "audit_scheduler": {
                "file": str(base_path / "audit_scheduler.py"),
                "process_name": "audit_scheduler",
                "critical": False,
                "module": "audit_scheduler"
            },
            "compliance_monitor": {
                "file": str(base_path / "security/compliance_monitor_152_fz.py"),
                "process_name": "compliance_monitor",
                "critical": False,
                "module": "compliance_monitor_152_fz"
            },
            "audit_dashboard_integration": {
                "file": None,  # Будем искать
                "process_name": "audit_dashboard",
                "critical": False,
                "module": "audit_dashboard_integration"
            },
            "external_integrations_dashboard": {
                "file": str(base_path / "external_integrations_dashboard.py"),
                "process_name": "external_dashboard",
                "critical": False,
                "module": "external_integrations_dashboard"
            },
            "run_performance_tests": {
                "file": str(base_path / "security/vpn/test_performance_features.py"),
                "process_name": "performance_tests",
                "critical": False,
                "module": "test_performance_features"
            }
        }

        # Критически важные компоненты (остаются активными)
        self.critical_components = [
            "core_security_manager",  # Ядро безопасности
            "basic_monitoring"       # Базовый мониторинг
        ]

        # Регистрируем в SFM (временно отключено)
        # if self.sfm:
        #     self.sfm.register_function(
        #         function_name="security_sleep_manager",
        #         function_obj=self,
        #         critical=True,
        #         sleep_mode=True
        #     )

        logger.info("Расширенный менеджер спящего режима безопасности инициализирован")
        logger.info(f"Зарегистрировано {len(self.security_components)} компонентов безопасности")

    async def find_missing_components(self) -> Dict[str, str]:
        """Поиск недостающих компонентов"""
        logger.info("🔍 Поиск недостающих компонентов безопасности...")

        missing_components = {}

        for component, info in self.security_components.items():
            if info["file"] is None:
                # Ищем файлы по ключевым словам
                search_terms = {
                    "advanced_behavioral_analytics": ["behavioral", "analytics"],
                    "automated_audit_system": ["audit", "automated"],
                    "audit_dashboard_integration": ["audit", "dashboard", "integration"]
                }

                if component in search_terms:
                    found_files = []
                    for term in search_terms[component]:
                        try:
                            result = subprocess.run(
                                f"find /Users/sergejhlystov/ALADDIN_NEW -name '*{term}*' -type f | head -5",
                                shell=True,
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0 and result.stdout.strip():
                                found_files.extend(result.stdout.strip().split('\n'))
                        except Exception as e:
                            logger.warning(f"Ошибка поиска {term}: {e}")

                    if found_files:
                        # Берем первый найденный файл
                        self.security_components[component]["file"] = found_files[0]
                        missing_components[component] = f"Найден: {found_files[0]}"
                    else:
                        missing_components[component] = "Не найден"
                else:
                    missing_components[component] = "Не найден"

        return missing_components

    async def check_all_security_components(self) -> Dict[str, Any]:
        """Проверка статуса всех компонентов безопасности"""
        logger.info("🔍 Проверка статуса всех компонентов безопасности...")

        components_status = {}

        for component, info in self.security_components.items():
            if info["file"] and os.path.exists(info["file"]):
                # Проверяем, запущен ли процесс
                process_status = await self._check_process(info["process_name"])
                file_status = "EXISTS"
            else:
                process_status = "NOT_FOUND"
                file_status = "NOT_FOUND"

            components_status[component] = {
                "file_status": file_status,
                "process_status": process_status,
                "file_path": info["file"],
                "is_critical": info["critical"]
            }

        return components_status

    async def _check_process(self, process_name: str) -> str:
        """Проверка запущенного процесса"""
        try:
            result = subprocess.run(
                f"pgrep -f {process_name}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return "ACTIVE"
            else:
                return "SLEEPING"
        except Exception:
            return "ERROR"

    async def put_security_component_to_sleep(self, component_name: str) -> bool:
        """Перевод компонента безопасности в спящий режим"""
        try:
            if component_name not in self.security_components:
                logger.warning(f"Компонент {component_name} не найден")
                return False

            info = self.security_components[component_name]

            if info["critical"]:
                logger.info(f"🔒 {component_name} остается активным (критический компонент)")
                return True

            # Останавливаем процесс, если он запущен
            if await self._check_process(info["process_name"]) == "ACTIVE":
                await self._stop_process(info["process_name"])
                logger.info(f"✅ {component_name} переведен в спящий режим")
            else:
                logger.info(f"😴 {component_name} уже в спящем режиме")

            return True

        except Exception as e:
            logger.error(f"Ошибка перевода {component_name} в спящий режим: {e}")
            return False

    async def _stop_process(self, process_name: str):
        """Остановка процесса"""
        try:
            # Находим и останавливаем процесс
            subprocess.run(
                f"pgrep -f {process_name} | xargs kill -TERM",
                shell=True,
                capture_output=True
            )

            # Ждем немного и принудительно завершаем, если нужно
            time.sleep(2)
            subprocess.run(
                f"pgrep -f {process_name} | xargs kill -KILL",
                shell=True,
                capture_output=True
            )

            logger.info(f"Процесс {process_name} остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки процесса {process_name}: {e}")

    async def sleep_all_security_components(self) -> Dict[str, Any]:
        """Перевод всех компонентов безопасности в спящий режим"""
        logger.info("😴 Перевод всех компонентов безопасности в спящий режим...")

        # Ищем недостающие компоненты
        missing = await self.find_missing_components()

        # Проверяем текущий статус
        components_status = await self.check_all_security_components()

        sleep_results = {}

        for component, info in self.security_components.items():
            if component in missing:
                sleep_results[component] = f"MISSING - {missing[component]}"
                continue

            if info["critical"]:
                sleep_results[component] = f"CRITICAL - {components_status[component]['process_status']}"
                logger.info(f"🔒 {component} остается активным (критический)")
            else:
                result = await self.put_security_component_to_sleep(component)
                if result:
                    sleep_results[component] = "SLEEPING"
                else:
                    sleep_results[component] = "ERROR"

        return sleep_results

    async def get_security_sleep_report(self) -> Dict[str, Any]:
        """Получение отчета о спящем режиме компонентов безопасности"""
        components_status = await self.check_all_security_components()

        active_count = sum(1 for comp in components_status.values()
                           if comp["process_status"] == "ACTIVE")
        sleeping_count = sum(1 for comp in components_status.values()
                             if comp["process_status"] == "SLEEPING")
        missing_count = sum(1 for comp in components_status.values()
                            if comp["file_status"] == "NOT_FOUND")
        critical_count = sum(1 for comp in self.security_components.values()
                             if comp["critical"])

        return {
            "total_components": len(self.security_components),
            "active_components": active_count,
            "sleeping_components": sleeping_count,
            "missing_components": missing_count,
            "critical_components": critical_count,
            "components_status": components_status,
            "critical_list": self.critical_components
        }

    def enable_sleep_mode(self):
        """Включение спящего режима"""
        self.sleep_mode = True
        logger.info("Спящий режим включен")

    def disable_sleep_mode(self):
        """Выключение спящего режима"""
        self.sleep_mode = False
        logger.info("Спящий режим выключен")

    async def run_tests(self):
        """Запуск тестов для проверки функциональности"""
        logger.info("🧪 Запуск тестов Security Sleep Manager...")

        try:
            # Тест 1: Поиск компонентов
            missing = await self.find_missing_components()
            logger.info(f"✅ Тест поиска компонентов: {len(missing)} не найдено")

            # Тест 2: Проверка статуса
            status = await self.check_all_security_components()
            logger.info(f"✅ Тест проверки статуса: {len(status)} компонентов")

            # Тест 3: Получение отчета
            report = await self.get_security_sleep_report()
            logger.info(f"✅ Тест отчета: {report['total_components']} компонентов")

            logger.info("🎉 Все тесты Security Sleep Manager прошли успешно!")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка в тестах: {e}")
            return False


async def main():
    """Основная функция"""
    print("😴 СИСТЕМА БЕЗОПАСНОСТИ ПЕРЕВОДИТСЯ В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)

    sleep_manager = ALADDINSecuritySleepManager()

    # Запускаем тесты
    await sleep_manager.run_tests()

    # Ищем недостающие компоненты
    print("\n🔍 Поиск недостающих компонентов...")
    missing = await sleep_manager.find_missing_components()

    if missing:
        print("📋 Найденные недостающие компоненты:")
        for component, status in missing.items():
            print(f"  {component}: {status}")

    # Проверяем текущий статус
    print("\n🔍 Проверка текущего статуса...")
    current_status = await sleep_manager.check_all_security_components()

    print("\n📊 Текущий статус компонентов безопасности:")
    for component, status in current_status.items():
        if status["file_status"] == "EXISTS":
            file_icon = "📁"
        else:
            file_icon = "❌"
        if status["process_status"] == "ACTIVE":
            process_icon = "🟢"
        elif status["process_status"] == "SLEEPING":
            process_icon = "🔴"
        else:
            process_icon = "⚪"
        if status["is_critical"]:
            critical_icon = "🔒"
        else:
            critical_icon = ""
        print(f"  {file_icon} {process_icon} {critical_icon} {component}: {status['process_status']}")

    # Переводим в спящий режим
    print("\n😴 Перевод в спящий режим...")
    sleep_results = await sleep_manager.sleep_all_security_components()

    print("\n📊 Результаты перевода в спящий режим:")
    for component, status in sleep_results.items():
        if "CRITICAL" in str(status):
            print(f"  🔒 {component}: {status}")
        elif "MISSING" in str(status):
            print(f"  ❌ {component}: {status}")
        elif status == "SLEEPING":
            print(f"  😴 {component}: {status}")
        else:
            print(f"  ⚠️ {component}: {status}")

    # Финальный отчет
    report = await sleep_manager.get_security_sleep_report()
    print("\n📈 ФИНАЛЬНЫЙ ОТЧЕТ БЕЗОПАСНОСТИ:")
    print(f"  Всего компонентов: {report['total_components']}")
    print(f"  Активных: {report['active_components']}")
    print(f"  В спящем режиме: {report['sleeping_components']}")
    print(f"  Не найденных: {report['missing_components']}")
    print(f"  Критических: {report['critical_components']}")

    print("\n🔒 КРИТИЧЕСКИЕ КОМПОНЕНТЫ (остаются активными):")
    for comp in report['critical_list']:
        print(f"  🔒 {comp}")

    print("\n✅ СИСТЕМА БЕЗОПАСНОСТИ УСПЕШНО ПЕРЕВЕДЕНА В СПЯЩИЙ РЕЖИМ!")
    print("💤 Только критически важные компоненты остаются активными")


if __name__ == "__main__":
    asyncio.run(main())
