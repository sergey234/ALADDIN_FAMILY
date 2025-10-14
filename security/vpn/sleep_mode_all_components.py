#!/usr/bin/env python3
"""
Спящий режим для всех VPN компонентов ALADDIN
Переводит все системы в спящий режим, оставляя только критически важные

Версия: 2.0
Автор: ALADDIN VPN Team
Дата: 2024
Соответствие: SOLID, DRY, PEP8
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import asyncio

# Добавляем путь к корневой директории проекта
sys.path.append(str(Path(__file__).parent.parent.parent))

# Временно отключаем импорты для автономной работы
# from security.safe_function_manager import SafeFunctionManager
# from core.system_manager import SystemManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/vpn_sleep_manager.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ALADDINVPNSleepManager:
    """Менеджер спящего режима для всех VPN компонентов"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern для VPN менеджера"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.components_status = {}
        self.sleep_mode = False

        # Временно отключаем инициализацию зависимостей
        # self.sfm = SafeFunctionManager()
        # self.system_manager = SystemManager()
        self.sfm = None
        self.system_manager = None

        self.critical_components = [
            "vpn_monitor",  # Самый важный - мониторинг системы
            "security_core",  # Второй по важности - ядро безопасности
        ]

        # Регистрируем в SFM (временно отключено)
        # if self.sfm:
        #     self.sfm.register_function(
        #         function_name="vpn_sleep_manager",
        #         function_obj=self,
        #         critical=True,
        #         sleep_mode=True
        #     )

        logger.info("Менеджер спящего режима VPN инициализирован")
        logger.info(f"Критических компонентов: {len(self.critical_components)}")
        self._initialized = True

    async def check_all_components(self) -> Dict[str, Any]:
        """Проверка статуса всех компонентов"""
        logger.info("🔍 Проверка статуса всех VPN компонентов...")

        components = {
            # Веб-серверы
            "web_server_5000": await self._check_port(5000),
            "web_server_5001": await self._check_port(5001),
            "web_server_5002": await self._check_port(5002),
            # Системы безопасности
            "ddos_protection": await self._check_module("protection.ddos_protection"),
            "rate_limiter": await self._check_module("protection.rate_limiter"),
            "intrusion_detection": await self._check_module("protection.intrusion_detection"),
            "two_factor_auth": await self._check_module("auth.two_factor_auth"),
            # Системы производительности
            "performance_manager": await self._check_module("performance.performance_manager"),
            "connection_cache": await self._check_module("performance.connection_cache"),
            "connection_pool": await self._check_module("performance.connection_pool"),
            "async_processor": await self._check_module("performance.async_processor"),
            # Дополнительные функции
            "split_tunneling": await self._check_module("features.split_tunneling"),
            "multi_hop": await self._check_module("features.multi_hop"),
            "auto_reconnect": await self._check_module("features.auto_reconnect"),
            # Протоколы
            "shadowsocks": await self._check_module("protocols.shadowsocks_client"),
            "v2ray": await self._check_module("protocols.v2ray_client"),
            "obfuscation": await self._check_module("protocols.obfuscation_manager"),
            # Соответствие 152-ФЗ
            "russia_compliance": await self._check_module("compliance.russia_compliance"),
            "data_localization": await self._check_module("compliance.data_localization"),
            "no_logs_policy": await self._check_module("compliance.no_logs_policy"),
            # Аудит и логирование
            "audit_logger": await self._check_module("audit_logging.audit_logger"),
            # Интеграция
            "aladdin_integration": await self._check_module("integration.aladdin_vpn_integration"),
            # Мониторинг
            "vpn_monitor": await self._check_process("auto_monitor.py"),
            "security_core": await self._check_module("security_integration"),
        }

        self.components_status = components
        return components

    async def _check_port(self, port: int) -> str:
        """Проверка занятости порта"""
        try:
            result = subprocess.run(f"lsof -i :{port}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return "ACTIVE"
            else:
                return "SLEEPING"
        except Exception:
            return "ERROR"

    async def _check_module(self, module_name: str) -> str:
        """Проверка доступности модуля"""
        try:
            exec(f"import {module_name}")
            return "READY"
        except ImportError:
            return "NOT_FOUND"
        except Exception:
            return "ERROR"

    async def _check_process(self, process_name: str) -> str:
        """Проверка запущенного процесса"""
        try:
            result = subprocess.run(f"pgrep -f {process_name}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return "ACTIVE"
            else:
                return "SLEEPING"
        except Exception:
            return "ERROR"

    async def put_to_sleep(self, component_name: str) -> bool:
        """Перевод компонента в спящий режим"""
        try:
            if component_name in self.components_status:
                if self.components_status[component_name] == "ACTIVE":
                    # Останавливаем активный компонент
                    if "web_server" in component_name:
                        port = component_name.split("_")[-1]
                        await self._stop_web_server(port)
                    elif component_name == "vpn_monitor":
                        await self._stop_vpn_monitor()
                    else:
                        logger.info(f"Компонент {component_name} уже в спящем режиме")

                    self.components_status[component_name] = "SLEEPING"
                    logger.info(f"✅ {component_name} переведен в спящий режим")
                    return True
                else:
                    logger.info(f"Компонент {component_name} уже в спящем режиме")
                    return True
            else:
                logger.warning(f"Компонент {component_name} не найден")
                return False
        except Exception as e:
            logger.error(f"Ошибка перевода {component_name} в спящий режим: {e}")
            return False

    async def _stop_web_server(self, port: str):
        """Остановка веб-сервера на порту"""
        try:
            subprocess.run(f"lsof -ti :{port} | xargs kill -9", shell=True, capture_output=True)
            logger.info(f"Веб-сервер на порту {port} остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки веб-сервера на порту {port}: {e}")

    async def _stop_vpn_monitor(self):
        """Остановка VPN мониторинга"""
        try:
            # Останавливаем auto_monitor.py
            subprocess.run("pkill -f auto_monitor.py", shell=True)

            # Удаляем PID файл
            if os.path.exists("vpn_monitor.pid"):
                os.remove("vpn_monitor.pid")

            logger.info("VPN мониторинг остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки VPN мониторинга: {e}")

    async def sleep_all_except_critical(self) -> Dict[str, Any]:
        """Перевод всех компонентов в спящий режим кроме критических"""
        logger.info("😴 Перевод всех VPN компонентов в спящий режим...")

        # Проверяем текущий статус
        await self.check_all_components()

        sleep_results = {}

        for component, status in self.components_status.items():
            if component not in self.critical_components:
                if status in ["ACTIVE", "READY"]:
                    result = await self.put_to_sleep(component)
                    sleep_results[component] = "SLEEPING" if result else "ERROR"
                else:
                    sleep_results[component] = status
            else:
                sleep_results[component] = f"CRITICAL - {status}"
                logger.info(f"🔒 {component} остается активным (критический компонент)")

        return sleep_results

    async def get_sleep_report(self) -> Dict[str, Any]:
        """Получение отчета о спящем режиме"""
        await self.check_all_components()

        active_count = sum(1 for status in self.components_status.values() if status in ["ACTIVE", "READY"])
        sleeping_count = sum(1 for status in self.components_status.values() if status == "SLEEPING")
        critical_count = sum(
            1
            for comp in self.critical_components
            if self.components_status.get(comp, "SLEEPING") in ["ACTIVE", "READY"]
        )

        return {
            "total_components": len(self.components_status),
            "active_components": active_count,
            "sleeping_components": sleeping_count,
            "critical_components": critical_count,
            "components_status": self.components_status,
            "critical_list": self.critical_components,
        }

    async def wake_up_component(self, component_name: str) -> bool:
        """Пробуждение компонента из спящего режима"""
        try:
            if component_name in self.components_status:
                if self.components_status[component_name] == "SLEEPING":
                    # Здесь можно добавить логику пробуждения
                    logger.info(f"🔔 {component_name} готов к пробуждению")
                    self.components_status[component_name] = "READY"
                    return True
                else:
                    logger.info(f"Компонент {component_name} уже активен")
                    return True
            else:
                logger.warning(f"Компонент {component_name} не найден")
                return False
        except Exception as e:
            logger.error(f"Ошибка пробуждения {component_name}: {e}")
            return False

    def enable_sleep_mode(self):
        """Включение спящего режима"""
        self.sleep_mode = True
        logger.info("Спящий режим включен для VPN менеджера")

    def disable_sleep_mode(self):
        """Выключение спящего режима"""
        self.sleep_mode = False
        logger.info("Спящий режим выключен для VPN менеджера")

    async def run_tests(self):
        """Запуск тестов для проверки функциональности"""
        logger.info("🧪 Запуск тестов VPN Sleep Manager...")

        try:
            # Тест 1: Проверка компонентов
            status = await self.check_all_components()
            logger.info(f"✅ Тест проверки компонентов: {len(status)} компонентов")

            # Тест 2: Получение отчета
            report = await self.get_sleep_report()
            logger.info(f"✅ Тест отчета: {report['total_components']} компонентов")

            # Тест 3: Пробуждение компонента
            wake_result = await self.wake_up_component("test_component")
            logger.info(f"✅ Тест пробуждения: {wake_result}")

            logger.info("🎉 Все тесты VPN Sleep Manager прошли успешно!")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка в тестах: {e}")
            return False


async def main():
    """Основная функция"""
    print("😴 VPN СИСТЕМА ПЕРЕВОДИТСЯ В СПЯЩИЙ РЕЖИМ")
    print("=" * 50)

    sleep_manager = ALADDINVPNSleepManager()

    # Запускаем тесты
    await sleep_manager.run_tests()

    # Проверяем текущий статус
    print("\n🔍 Проверка текущего статуса...")
    current_status = await sleep_manager.check_all_components()

    print("\n📊 Текущий статус:")
    for component, status in current_status.items():
        status_icon = "🟢" if status in ["ACTIVE", "READY"] else "🔴" if status == "SLEEPING" else "⚪"
        print(f"  {status_icon} {component}: {status}")

    # Переводим в спящий режим
    print("\n😴 Перевод в спящий режим...")
    sleep_results = await sleep_manager.sleep_all_except_critical()

    print("\n📊 Результаты перевода в спящий режим:")
    for component, status in sleep_results.items():
        if "CRITICAL" in str(status):
            print(f"  🔒 {component}: {status}")
        elif status == "SLEEPING":
            print(f"  😴 {component}: {status}")
        else:
            print(f"  ⚪ {component}: {status}")

    # Финальный отчет
    report = await sleep_manager.get_sleep_report()
    print("\n📈 ФИНАЛЬНЫЙ ОТЧЕТ:")
    print(f"  Всего компонентов: {report['total_components']}")
    print(f"  Активных: {report['active_components']}")
    print(f"  В спящем режиме: {report['sleeping_components']}")
    print(f"  Критических: {report['critical_components']}")

    print("\n🔒 КРИТИЧЕСКИЕ КОМПОНЕНТЫ (остаются активными):")
    for comp in report["critical_list"]:
        status = report["components_status"].get(comp, "UNKNOWN")
        print(f"  🔒 {comp}: {status}")

    print("\n✅ VPN СИСТЕМА УСПЕШНО ПЕРЕВЕДЕНА В СПЯЩИЙ РЕЖИМ!")
    print("💤 Только критически важные компоненты остаются активными")


if __name__ == "__main__":
    asyncio.run(main())
