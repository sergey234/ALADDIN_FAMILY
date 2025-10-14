#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Security Orchestrator - Единый оркестратор безопасности
Интегрирует все компоненты ALADDIN Security System в единую систему

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-28
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from core.base import ComponentStatus, SecurityBase
from security.async_io_manager import AsyncIOManager
from security.circuit_breaker import SmartCircuitBreaker
from security.microservices.load_balancer import LoadBalancer
from security.microservices.service_mesh_manager import ServiceMeshManager

# Импорты всех компонентов
from security.safe_function_manager import SafeFunctionManager
from security.scaling.auto_scaling_engine import AutoScalingEngine
from security.zero_trust_manager import TrustLevel, ZeroTrustManager


class UnifiedSecurityOrchestrator(SecurityBase):
    """
    Единый оркестратор безопасности ALADDIN
    Координирует работу всех компонентов системы безопасности
    """

    def __init__(
        self,
        name: str = "UnifiedSecurityOrchestrator",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Инициализация всех компонентов
        self.sfm = SafeFunctionManager(f"{name}_SFM", config)
        self.async_io = AsyncIOManager(max_concurrent_operations=100)
        self.scaling_engine = AutoScalingEngine(f"{name}_Scaling")
        self.load_balancer = LoadBalancer()
        self.zero_trust = ZeroTrustManager()
        self.circuit_breaker = SmartCircuitBreaker(f"{name}_CircuitBreaker")
        self.service_mesh = ServiceMeshManager(f"{name}_ServiceMesh")

        # Состояние оркестратора
        self.is_initialized = False
        self.performance_metrics = {}
        self.security_events = []

        # Конфигурация интеграции
        self.integration_config = {
            "enable_zero_trust": True,
            "enable_load_balancing": True,
            "enable_auto_scaling": True,
            "enable_circuit_breaking": True,
            "enable_service_mesh": True,
            "trust_threshold": TrustLevel.MEDIUM,
            "max_concurrent_requests": 1000,
            "response_timeout": 30.0,
        }

        if config:
            self.integration_config.update(config.get("integration", {}))

    async def initialize(self) -> bool:
        """Инициализация всех компонентов"""
        try:
            self.log_activity("Инициализация Unified Security Orchestrator")
            self.status = ComponentStatus.INITIALIZING

            # Инициализация компонентов параллельно
            init_tasks = [
                self.sfm.initialize(),
                self.async_io.start(),
                self.scaling_engine.initialize(),
                self.load_balancer.initialize(),
                self.zero_trust.initialize(),
                self.service_mesh.initialize(),
            ]

            results = await asyncio.gather(*init_tasks, return_exceptions=True)

            # Проверка результатов
            failed_components = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    component_names = [
                        "SFM",
                        "AsyncIO",
                        "Scaling",
                        "LoadBalancer",
                        "ZeroTrust",
                        "ServiceMesh",
                    ]
                    failed_components.append(component_names[i])
                    self.log_activity(
                        f"Ошибка инициализации {component_names[i]}: {result}",
                        "error",
                    )

            if failed_components:
                self.log_activity(
                    f"Не удалось инициализировать: {', '.join(failed_components)}",
                    "error",
                )
                return False

            self.is_initialized = True
            self.status = ComponentStatus.RUNNING
            self.log_activity(
                "Unified Security Orchestrator успешно инициализирован"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Критическая ошибка инициализации: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    async def execute_function_with_full_security(
        self,
        function_id: str,
        params: Optional[Dict[str, Any]] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Any, str]:
        """
        Выполнение функции с полной проверкой безопасности

        Args:
            function_id: ID функции
            params: Параметры выполнения
            request_context: Контекст запроса для Zero Trust

        Returns:
            Tuple[bool, Any, str]: (успех, результат, сообщение)
        """
        if not self.is_initialized:
            return False, None, "Оркестратор не инициализирован"

        start_time = time.time()
        security_checks_passed = True
        security_events = []

        try:
            # 1. Zero Trust проверка
            if (
                self.integration_config["enable_zero_trust"]
                and request_context
            ):
                trust_level = await self.zero_trust.verify_request(
                    request_context
                )
                if (
                    trust_level.value
                    < self.integration_config["trust_threshold"].value
                ):
                    security_events.append(
                        f"Zero Trust: недостаточный уровень доверия ({trust_level.value})"
                    )
                    security_checks_passed = False

            # 2. Circuit Breaker проверка
            if self.integration_config["enable_circuit_breaking"]:
                if not await self.circuit_breaker.can_execute(function_id):
                    security_events.append(
                        "Circuit Breaker: функция заблокирована"
                    )
                    security_checks_passed = False

            # 3. Load Balancer выбор узла
            if self.integration_config["enable_load_balancing"]:
                target_node = await self.load_balancer.select_node(function_id)
                if not target_node:
                    security_events.append(
                        "Load Balancer: нет доступных узлов"
                    )
                    security_checks_passed = False

            # 4. Проверка масштабирования
            if self.integration_config["enable_auto_scaling"]:
                scaling_decision = (
                    await self.scaling_engine.evaluate_scaling_need()
                )
                if scaling_decision.action == "scale_up":
                    await self.scaling_engine.scale_up()
                    security_events.append(
                        "Auto Scaling: масштабирование вверх"
                    )

            if not security_checks_passed:
                self._log_security_event(
                    "SECURITY_BLOCKED",
                    function_id,
                    {
                        "events": security_events,
                        "request_context": request_context,
                    },
                )
                return (
                    False,
                    None,
                    f"Блокировано системой безопасности: {'; '.join(security_events)}",
                )

            # 5. Выполнение функции через SFM
            success, result, message = await self.sfm.execute_function_async(
                function_id, params
            )

            # 6. Обновление метрик
            execution_time = time.time() - start_time
            await self._update_performance_metrics(
                function_id, success, execution_time
            )

            # 7. Обновление Circuit Breaker
            if self.integration_config["enable_circuit_breaking"]:
                await self.circuit_breaker.record_result(function_id, success)

            return success, result, message

        except Exception as e:
            self.log_activity(
                f"Ошибка выполнения функции {function_id}: {e}", "error"
            )
            return False, None, f"Системная ошибка: {e}"

    async def _update_performance_metrics(
        self, function_id: str, success: bool, execution_time: float
    ):
        """Обновление метрик производительности"""
        if function_id not in self.performance_metrics:
            self.performance_metrics[function_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0.0,
                "last_execution": None,
            }

        metrics = self.performance_metrics[function_id]
        metrics["total_executions"] += 1
        metrics["last_execution"] = datetime.now()

        if success:
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1

        # Обновление среднего времени выполнения
        total_time = metrics["average_execution_time"] * (
            metrics["total_executions"] - 1
        )
        metrics["average_execution_time"] = (
            total_time + execution_time
        ) / metrics["total_executions"]

    def _log_security_event(
        self, event_type: str, function_id: str, details: Dict[str, Any]
    ):
        """Логирование событий безопасности"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "function_id": function_id,
            "details": details,
        }
        self.security_events.append(event)
        self.log_activity(
            f"Security Event: {event_type} for {function_id}", "warning"
        )

    async def get_system_health(self) -> Dict[str, Any]:
        """Получение состояния всей системы"""
        if not self.is_initialized:
            return {"status": "not_initialized", "components": {}}

        health_data = {
            "orchestrator_status": self.status.value,
            "is_initialized": self.is_initialized,
            "components": {
                "sfm": await self.sfm.get_status(),
                "async_io": "running" if self.async_io._running else "stopped",
                "scaling_engine": await self.scaling_engine.get_status(),
                "load_balancer": await self.load_balancer.get_health_status(),
                "zero_trust": "active",
                "circuit_breaker": self.circuit_breaker.state.value,
                "service_mesh": await self.service_mesh.get_status(),
            },
            "performance_metrics": self.performance_metrics,
            "security_events_count": len(self.security_events),
            "integration_config": self.integration_config,
        }

        return health_data

    async def shutdown(self):
        """Корректное завершение работы всех компонентов"""
        self.log_activity("Завершение работы Unified Security Orchestrator")

        try:
            await self.async_io.stop()
            await self.scaling_engine.shutdown()
            await self.load_balancer.shutdown()
            await self.service_mesh.shutdown()

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                "Unified Security Orchestrator успешно остановлен"
            )

        except Exception as e:
            self.log_activity(f"Ошибка при завершении работы: {e}", "error")


# Пример использования
async def main():
    """Пример использования Unified Security Orchestrator"""
    orchestrator = UnifiedSecurityOrchestrator()

    # Инициализация
    if await orchestrator.initialize():
        print("✅ Оркестратор инициализирован")

        # Выполнение функции с полной проверкой безопасности
        request_context = {
            "user_id": "user123",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "request_id": "req_456",
        }

        success, result, message = (
            await orchestrator.execute_function_with_full_security(
                "test_function", {"param1": "value1"}, request_context
            )
        )

        print(f"Результат выполнения: {success}, {result}, {message}")

        # Получение состояния системы
        health = await orchestrator.get_system_health()
        print(f"Состояние системы: {health}")

        # Завершение работы
        await orchestrator.shutdown()
    else:
        print("❌ Ошибка инициализации оркестратора")


if __name__ == "__main__":
    asyncio.run(main())
