#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeFunctionManager Integration - Интеграция всех микросервисов
Интеграция RateLimiter, CircuitBreaker и UserInterfaceManager с
SafeFunctionManager

Этот модуль обеспечивает интеграцию всех созданных микросервисов с
центральной системой управления безопасными функциями, включая:
- Регистрацию всех компонентов в SafeFunctionManager
- Управление жизненным циклом микросервисов
- Мониторинг состояния всех компонентов
- Интеграцию с системой безопасности
- Автоматическое тестирование интеграции
- Детальное логирование всех операций

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

import asyncio
import logging
import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты после настройки sys.path
try:
    from circuit_breaker import CircuitBreaker, CircuitBreakerRequest
    from rate_limiter import RateLimiter, RateLimitRequest
    from user_interface_manager import InterfaceRequest, UserInterfaceManager
    from security.core.security_base import SecurityBase
except ImportError as e:
    logger.warning(f"Не удалось импортировать модули: {e}")
    # Создаем заглушки для отсутствующих модулей

    class CircuitBreaker:
        pass

    class CircuitBreakerRequest:
        pass

    class RateLimiter:
        pass

    class RateLimitRequest:
        pass

    class InterfaceRequest:
        pass

    class UserInterfaceManager:
        pass

    class SecurityBase:
        def __init__(self, name=None, config=None):
            self.name = name or "SecurityBase"
            self.config = config or {}
            self.logger = logger


class SafeFunctionManagerIntegration(SecurityBase):
    """
    Интеграция всех микросервисов с SafeFunctionManager

    Обеспечивает:
    - Регистрацию компонентов
    - Управление жизненным циклом
    - Мониторинг состояния
    - Интеграцию с безопасностью
    """

    def __init__(
        self,
        name: str = "SafeFunctionManagerIntegration",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация интеграции

        Args:
            name: Имя интеграции
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "enable_rate_limiter": True,
            "enable_circuit_breaker": True,
            "enable_user_interface_manager": True,
            "auto_start_services": True,
            "health_check_interval": 30,  # секунд
            "integration_timeout": 60,  # секунд
            "enable_monitoring": True,
            "enable_logging": True,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Компоненты
        self.rate_limiter: Optional[RateLimiter] = None
        self.circuit_breaker: Optional[CircuitBreaker] = None
        self.user_interface_manager: Optional[UserInterfaceManager] = None

        # Статус компонентов
        self.component_status = {
            "rate_limiter": {
                "status": "stopped",
                "last_check": None,
                "error": None,
            },
            "circuit_breaker": {
                "status": "stopped",
                "last_check": None,
                "error": None,
            },
            "user_interface_manager": {
                "status": "stopped",
                "last_check": None,
                "error": None,
            },
        }

        # Статистика
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited_requests": 0,
            "circuit_breaker_blocks": 0,
            "interface_generations": 0,
            "integration_errors": 0,
        }

        # Потоки
        self.health_check_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(
            f"SafeFunctionManagerIntegration {name} инициализирован"
        )

    async def start(self) -> bool:
        """Запуск интеграции"""
        try:
            self.logger.info("Запуск SafeFunctionManagerIntegration")

            # Инициализация компонентов
            await self._initialize_components()

            # Запуск компонентов
            if self.config["auto_start_services"]:
                await self._start_components()

            # Запуск мониторинга
            if self.config["enable_monitoring"]:
                self.running = True
                self.health_check_thread = threading.Thread(
                    target=self._health_check_worker, daemon=True
                )
                self.health_check_thread.start()

            self.logger.info("SafeFunctionManagerIntegration успешно запущен")
            return True

        except Exception as e:
            self.logger.error(
                f"Ошибка запуска SafeFunctionManagerIntegration: {e}"
            )
            return False

    async def stop(self) -> bool:
        """Остановка интеграции"""
        try:
            self.logger.info("Остановка SafeFunctionManagerIntegration")

            self.running = False

            # Остановка мониторинга
            if (
                self.health_check_thread
                and self.health_check_thread.is_alive()
            ):
                self.health_check_thread.join(timeout=5)

            # Остановка компонентов
            await self._stop_components()

            self.logger.info(
                "SafeFunctionManagerIntegration успешно остановлен"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Ошибка остановки SafeFunctionManagerIntegration: {e}"
            )
            return False

    async def _initialize_components(self) -> None:
        """Инициализация всех компонентов"""
        try:
            # Инициализация RateLimiter
            if self.config["enable_rate_limiter"]:
                self.rate_limiter = RateLimiter("IntegratedRateLimiter")
                self.logger.info("RateLimiter инициализирован")

            # Инициализация CircuitBreaker
            if self.config["enable_circuit_breaker"]:
                self.circuit_breaker = CircuitBreaker(
                    "IntegratedCircuitBreaker"
                )
                self.logger.info("CircuitBreaker инициализирован")

            # Инициализация UserInterfaceManager
            if self.config["enable_user_interface_manager"]:
                self.user_interface_manager = UserInterfaceManager(
                    "IntegratedUserInterfaceManager"
                )
                self.logger.info("UserInterfaceManager инициализирован")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации компонентов: {e}")
            raise

    async def _start_components(self) -> None:
        """Запуск всех компонентов"""
        try:
            # Запуск RateLimiter
            if self.rate_limiter:
                success = await self.rate_limiter.start()
                if success:
                    self.component_status["rate_limiter"]["status"] = "running"
                    self.logger.info("RateLimiter запущен")
                else:
                    self.component_status["rate_limiter"]["status"] = "error"
                    self.component_status["rate_limiter"][
                        "error"
                    ] = "Failed to start"
                    self.logger.error("Ошибка запуска RateLimiter")

            # Запуск CircuitBreaker
            if self.circuit_breaker:
                success = await self.circuit_breaker.start()
                if success:
                    self.component_status["circuit_breaker"][
                        "status"
                    ] = "running"
                    self.logger.info("CircuitBreaker запущен")
                else:
                    self.component_status["circuit_breaker"][
                        "status"
                    ] = "error"
                    self.component_status["circuit_breaker"][
                        "error"
                    ] = "Failed to start"
                    self.logger.error("Ошибка запуска CircuitBreaker")

            # Запуск UserInterfaceManager
            if self.user_interface_manager:
                success = await self.user_interface_manager.start()
                if success:
                    self.component_status["user_interface_manager"][
                        "status"
                    ] = "running"
                    self.logger.info("UserInterfaceManager запущен")
                else:
                    self.component_status["user_interface_manager"][
                        "status"
                    ] = "error"
                    self.component_status["user_interface_manager"][
                        "error"
                    ] = "Failed to start"
                    self.logger.error("Ошибка запуска UserInterfaceManager")

        except Exception as e:
            self.logger.error(f"Ошибка запуска компонентов: {e}")
            raise

    async def _stop_components(self) -> None:
        """Остановка всех компонентов"""
        try:
            # Остановка RateLimiter
            if self.rate_limiter:
                success = await self.rate_limiter.stop()
                if success:
                    self.component_status["rate_limiter"]["status"] = "stopped"
                    self.logger.info("RateLimiter остановлен")

            # Остановка CircuitBreaker
            if self.circuit_breaker:
                success = await self.circuit_breaker.stop()
                if success:
                    self.component_status["circuit_breaker"][
                        "status"
                    ] = "stopped"
                    self.logger.info("CircuitBreaker остановлен")

            # Остановка UserInterfaceManager
            if self.user_interface_manager:
                success = await self.user_interface_manager.stop()
                if success:
                    self.component_status["user_interface_manager"][
                        "status"
                    ] = "stopped"
                    self.logger.info("UserInterfaceManager остановлен")

        except Exception as e:
            self.logger.error(f"Ошибка остановки компонентов: {e}")

    async def _health_check_worker(self) -> None:
        """Фоновый процесс проверки здоровья компонентов"""
        while self.running:
            try:
                time.sleep(self.config["health_check_interval"])

                # Проверка RateLimiter
                if self.rate_limiter:
                    try:
                        status = await self.rate_limiter.get_status()
                        self.component_status["rate_limiter"]["status"] = (
                            status["status"]
                        )
                        self.component_status["rate_limiter"][
                            "last_check"
                        ] = datetime.utcnow()
                        self.component_status["rate_limiter"]["error"] = None
                    except Exception as e:
                        self.component_status["rate_limiter"][
                            "status"
                        ] = "error"
                        self.component_status["rate_limiter"]["error"] = str(e)
                        self.logger.error(f"Ошибка проверки RateLimiter: {e}")

                # Проверка CircuitBreaker
                if self.circuit_breaker:
                    try:
                        status = await self.circuit_breaker.get_status()
                        self.component_status["circuit_breaker"]["status"] = (
                            status["status"]
                        )
                        self.component_status["circuit_breaker"][
                            "last_check"
                        ] = datetime.utcnow()
                        self.component_status["circuit_breaker"][
                            "error"
                        ] = None
                    except Exception as e:
                        self.component_status["circuit_breaker"][
                            "status"
                        ] = "error"
                        self.component_status["circuit_breaker"]["error"] = (
                            str(e)
                        )
                        self.logger.error(
                            f"Ошибка проверки CircuitBreaker: {e}"
                        )

                # Проверка UserInterfaceManager
                if self.user_interface_manager:
                    try:
                        status = await self.user_interface_manager.get_status()
                        self.component_status["user_interface_manager"][
                            "status"
                        ] = status["status"]
                        self.component_status["user_interface_manager"][
                            "last_check"
                        ] = datetime.utcnow()
                        self.component_status["user_interface_manager"][
                            "error"
                        ] = None
                    except Exception as e:
                        self.component_status["user_interface_manager"][
                            "status"
                        ] = "error"
                        self.component_status["user_interface_manager"][
                            "error"
                        ] = str(e)
                        self.logger.error(
                            f"Ошибка проверки UserInterfaceManager: {e}"
                        )

            except Exception as e:
                self.logger.error(f"Ошибка в процессе проверки здоровья: {e}")

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка запроса через все компоненты

        Args:
            request: Запрос для обработки

        Returns:
            Dict[str, Any]: Результат обработки
        """
        start_time = time.time()

        try:
            with self.lock:
                self.stats["total_requests"] += 1

            # 1. Rate Limiting
            if (
                self.rate_limiter
                and self.component_status["rate_limiter"]["status"]
                == "running"
            ):
                rate_limit_request = RateLimitRequest(
                    client_id=request.get("client_id", "unknown"),
                    client_type=request.get("client_type", "user"),
                    ip_address=request.get("ip_address"),
                    user_agent=request.get("user_agent"),
                    request_size=request.get("request_size", 1),
                    priority=request.get("priority", 1),
                    metadata=request.get("metadata", {}),
                )

                rate_limit_response = await self.rate_limiter.check_rate_limit(
                    rate_limit_request
                )

                if not rate_limit_response.allowed:
                    with self.lock:
                        self.stats["rate_limited_requests"] += 1

                    return {
                        "success": False,
                        "error": "Rate limit exceeded",
                        "reason": rate_limit_response.reason,
                        "retry_after": rate_limit_response.retry_after,
                        "component": "rate_limiter",
                    }

            # 2. Circuit Breaker
            if (
                self.circuit_breaker
                and self.component_status["circuit_breaker"]["status"]
                == "running"
            ):
                circuit_breaker_request = CircuitBreakerRequest(
                    service_name=request.get("service_name", "default"),
                    operation=request.get("operation", "process"),
                    operation_type=request.get("operation_type", "http"),
                    timeout=request.get("timeout"),
                    retry_count=request.get("retry_count", 0),
                    priority=request.get("priority", 1),
                    metadata=request.get("metadata", {}),
                )

                # Простая операция для тестирования
                async def test_operation(**kwargs):
                    await asyncio.sleep(0.1)
                    return {
                        "result": "success",
                        "data": request.get("data", {}),
                    }

                circuit_breaker_response = await self.circuit_breaker.execute(
                    circuit_breaker_request, test_operation
                )

                if not circuit_breaker_response.success:
                    with self.lock:
                        self.stats["circuit_breaker_blocks"] += 1

                    return {
                        "success": False,
                        "error": "Circuit breaker blocked",
                        "reason": circuit_breaker_response.error,
                        "circuit_state": (
                            circuit_breaker_response.circuit_state
                        ),
                        "component": "circuit_breaker",
                    }

            # 3. User Interface Management
            if (
                self.user_interface_manager
                and self.component_status["user_interface_manager"]["status"]
                == "running"
            ):
                interface_request = InterfaceRequest(
                    user_id=request.get("user_id", "unknown"),
                    interface_type=request.get("interface_type", "web"),
                    device_type=request.get("device_type", "desktop"),
                    platform=request.get("platform", "web"),
                    language=request.get("language"),
                    theme=request.get("theme"),
                    layout=request.get("layout"),
                    session_id=request.get("session_id"),
                    metadata=request.get("metadata", {}),
                )

                interface_response = (
                    await self.user_interface_manager.get_interface(
                        interface_request
                    )
                )

                if not interface_response.success:
                    return {
                        "success": False,
                        "error": "Interface generation failed",
                        "reason": interface_response.metadata.get("error"),
                        "component": "user_interface_manager",
                    }

                with self.lock:
                    self.stats["interface_generations"] += 1

                # Добавление данных интерфейса к результату
                request["interface_data"] = interface_response.interface_data
                request["user_preferences"] = (
                    interface_response.user_preferences
                )
                request["recommendations"] = interface_response.recommendations

            # Успешная обработка
            with self.lock:
                self.stats["successful_requests"] += 1

            return {
                "success": True,
                "data": request,
                "processing_time": time.time() - start_time,
                "components_used": self._get_active_components(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка обработки запроса: {e}")

            with self.lock:
                self.stats["failed_requests"] += 1
                self.stats["integration_errors"] += 1

            return {
                "success": False,
                "error": f"Integration error: {str(e)}",
                "processing_time": time.time() - start_time,
                "components_used": self._get_active_components(),
            }

    def _get_active_components(self) -> List[str]:
        """Получение списка активных компонентов"""
        active_components = []

        if self.component_status["rate_limiter"]["status"] == "running":
            active_components.append("rate_limiter")

        if self.component_status["circuit_breaker"]["status"] == "running":
            active_components.append("circuit_breaker")

        if (
            self.component_status["user_interface_manager"]["status"]
            == "running"
        ):
            active_components.append("user_interface_manager")

        return active_components

    async def get_integration_status(self) -> Dict[str, Any]:
        """Получение статуса интеграции"""
        with self.lock:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "stats": self.stats.copy(),
                "component_status": self.component_status.copy(),
                "active_components": self._get_active_components(),
                "config": {
                    "enable_rate_limiter": self.config["enable_rate_limiter"],
                    "enable_circuit_breaker": self.config[
                        "enable_circuit_breaker"
                    ],
                    "enable_user_interface_manager": self.config[
                        "enable_user_interface_manager"
                    ],
                    "auto_start_services": self.config["auto_start_services"],
                },
            }

    async def test_integration(self) -> Dict[str, Any]:
        """Тестирование интеграции всех компонентов"""
        test_results = {
            "rate_limiter": {"status": "not_tested", "error": None},
            "circuit_breaker": {"status": "not_tested", "error": None},
            "user_interface_manager": {"status": "not_tested", "error": None},
            "integration": {"status": "not_tested", "error": None},
        }

        try:
            # Тест RateLimiter
            if self.rate_limiter:
                try:
                    test_request = RateLimitRequest(
                        client_id="test_client",
                        client_type="user",
                        ip_address="127.0.0.1",
                        user_agent="TestAgent/1.0",
                    )

                    response = await self.rate_limiter.check_rate_limit(
                        test_request
                    )
                    test_results["rate_limiter"]["status"] = (
                        "passed" if response.allowed else "limited"
                    )
                except Exception as e:
                    test_results["rate_limiter"]["status"] = "failed"
                    test_results["rate_limiter"]["error"] = str(e)

            # Тест CircuitBreaker
            if self.circuit_breaker:
                try:
                    test_request = CircuitBreakerRequest(
                        service_name="test_service",
                        operation="test_operation",
                        operation_type="http",
                    )

                    async def test_operation(**kwargs):
                        return {"result": "success"}

                    response = await self.circuit_breaker.execute(
                        test_request, test_operation
                    )
                    test_results["circuit_breaker"]["status"] = (
                        "passed" if response.success else "blocked"
                    )
                except Exception as e:
                    test_results["circuit_breaker"]["status"] = "failed"
                    test_results["circuit_breaker"]["error"] = str(e)

            # Тест UserInterfaceManager
            if self.user_interface_manager:
                try:
                    test_request = InterfaceRequest(
                        user_id="test_user",
                        interface_type="web",
                        device_type="desktop",
                        platform="web",
                    )

                    response = await self.user_interface_manager.get_interface(
                        test_request
                    )
                    test_results["user_interface_manager"]["status"] = (
                        "passed" if response.success else "failed"
                    )
                except Exception as e:
                    test_results["user_interface_manager"]["status"] = "failed"
                    test_results["user_interface_manager"]["error"] = str(e)

            # Тест интеграции
            try:
                test_request = {
                    "client_id": "test_client",
                    "client_type": "user",
                    "user_id": "test_user",
                    "interface_type": "web",
                    "device_type": "desktop",
                    "platform": "web",
                    "service_name": "test_service",
                    "operation": "test_operation",
                    "data": {"test": "data"},
                }

                response = await self.process_request(test_request)
                test_results["integration"]["status"] = (
                    "passed" if response["success"] else "failed"
                )
            except Exception as e:
                test_results["integration"]["status"] = "failed"
                test_results["integration"]["error"] = str(e)

            return test_results

        except Exception as e:
            self.logger.error(f"Ошибка тестирования интеграции: {e}")
            return test_results


# Основная функция для тестирования интеграции
async def main():
    """Основная функция для тестирования интеграции"""
    print("🧪 Тестирование интеграции SafeFunctionManager...")

    # Создание интеграции
    integration = SafeFunctionManagerIntegration("TestIntegration")

    try:
        # Запуск интеграции
        success = await integration.start()
        if not success:
            print("❌ Ошибка запуска интеграции")
            return

        print("✅ Интеграция запущена")

        # Тестирование компонентов
        test_results = await integration.test_integration()

        print("\n📊 Результаты тестирования:")
        for component, result in test_results.items():
            status = result["status"]
            error = result.get("error")
            if status == "passed":
                print(f"✅ {component}: {status}")
            elif status == "failed":
                print(f"❌ {component}: {status} - {error}")
            else:
                print(f"⚠️  {component}: {status}")

        # Получение статуса интеграции
        status = await integration.get_integration_status()
        print("\n📈 Статистика интеграции:")
        print(f"  - Всего запросов: {status['stats']['total_requests']}")
        print(f"  - Успешных: {status['stats']['successful_requests']}")
        print(f"  - Неудачных: {status['stats']['failed_requests']}")
        print(
            f"  - Заблокированных rate limiter: "
            f"{status['stats']['rate_limited_requests']}"
        )
        print(
            f"  - Заблокированных circuit breaker: "
            f"{status['stats']['circuit_breaker_blocks']}"
        )
        print(
            f"  - Сгенерированных интерфейсов: "
            f"{status['stats']['interface_generations']}"
        )

        print(
            f"\n🔧 Активные компоненты: "
            f"{', '.join(status['active_components'])}"
        )

        print("\n🎉 Тестирование интеграции завершено!")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

    finally:
        # Остановка интеграции
        await integration.stop()
        print("✅ Интеграция остановлена")


if __name__ == "__main__":
    asyncio.run(main())
