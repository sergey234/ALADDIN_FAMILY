#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer - Оптимизатор производительности
Автоматическая настройка параметров для максимальной производительности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-28
"""

import asyncio
import json
import psutil
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from core.base import SecurityBase


@dataclass
class PerformanceProfile:
    """Профиль производительности системы"""
    cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float
    disk_io_speed: float
    network_bandwidth: float
    current_load: float
    recommended_concurrency: int
    recommended_cache_size: int
    recommended_thread_pool_size: int


@dataclass
class OptimizedConfig:
    """Оптимизированная конфигурация"""
    # SFM параметры
    max_concurrent_functions: int
    function_timeout: int
    cache_ttl: int
    sleep_check_interval: int
    max_thread_pool_workers: int

    # Scaling параметры
    max_instances: int
    min_instances: int
    cpu_threshold: float
    memory_threshold: float
    scale_up_cooldown: int
    scale_down_cooldown: int

    # Load Balancer параметры
    health_check_interval: int
    max_retries: int
    timeout: int

    # Circuit Breaker параметры
    failure_threshold: int
    success_threshold: int
    recovery_timeout: int

    # Zero Trust параметры
    trust_verification_timeout: int
    max_concurrent_verifications: int


class PerformanceOptimizer(SecurityBase):
    """
    Оптимизатор производительности ALADDIN Security System
    Автоматически настраивает параметры для максимальной производительности
    """

    def __init__(self, name: str = "PerformanceOptimizer",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        self.performance_history = []
        self.optimization_rules = self._load_optimization_rules()
        self.current_profile = None
        self.optimized_config = None

        # Мониторинг производительности
        self.monitoring_interval = 60  # секунд
        self.monitoring_active = False

    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Загрузка правил оптимизации"""
        return {
            "cpu_optimization": {
                "high_cpu_threshold": 80.0,
                "medium_cpu_threshold": 50.0,
                "low_cpu_threshold": 20.0,
                "concurrency_multipliers": {
                    "high": 0.5,    # Уменьшить нагрузку при высокой загрузке CPU
                    "medium": 1.0,  # Стандартная нагрузка
                    "low": 1.5      # Увеличить нагрузку при низкой загрузке CPU
                }
            },
            "memory_optimization": {
                "high_memory_threshold": 85.0,
                "medium_memory_threshold": 60.0,
                "low_memory_threshold": 30.0,
                "cache_size_multipliers": {
                    "high": 0.3,    # Сильно уменьшить кэш при нехватке памяти
                    "medium": 0.7,  # Умеренно уменьшить кэш
                    "low": 1.2      # Увеличить кэш при избытке памяти
                }
            },
            "network_optimization": {
                "high_bandwidth_threshold": 1000,  # Mbps
                "medium_bandwidth_threshold": 100,  # Mbps
                "low_bandwidth_threshold": 10,     # Mbps
                "timeout_multipliers": {
                    "high": 0.8,    # Быстрее таймауты при хорошей сети
                    "medium": 1.0,  # Стандартные таймауты
                    "low": 1.5      # Увеличить таймауты при медленной сети
                }
            }
        }

    async def analyze_system_performance(self) -> PerformanceProfile:
        """Анализ текущей производительности системы"""
        try:
            # Получение системной информации
            cpu_cores = psutil.cpu_count(logical=True)
            memory = psutil.virtual_memory()
            disk = psutil.disk_io_counters()

            # Измерение производительности
            await asyncio.sleep(1)  # Измеряем за 1 секунду

            # Расчет метрик
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_gb = memory.total / (1024**3)
            available_memory_gb = memory.available / (1024**3)

            # Оценка производительности диска (упрощенная)
            disk_io_speed = disk.read_bytes + disk.write_bytes if disk else 0

            # Оценка сетевой производительности (упрощенная)
            network_bandwidth = 1000  # Предполагаем 1 Gbps

            # Рекомендации по конcurrency
            if cpu_percent < 20:
                recommended_concurrency = cpu_cores * 4
            elif cpu_percent < 50:
                recommended_concurrency = cpu_cores * 2
            else:
                recommended_concurrency = cpu_cores

            # Рекомендации по размеру кэша
            if available_memory_gb > 8:
                recommended_cache_size = int(available_memory_gb * 0.3 * 1024)  # 30% памяти в MB
            elif available_memory_gb > 4:
                recommended_cache_size = int(available_memory_gb * 0.2 * 1024)  # 20% памяти в MB
            else:
                recommended_cache_size = int(available_memory_gb * 0.1 * 1024)  # 10% памяти в MB

            # Рекомендации по размеру пула потоков
            recommended_thread_pool_size = min(cpu_cores * 2, 50)

            profile = PerformanceProfile(
                cpu_cores=cpu_cores,
                total_memory_gb=memory_gb,
                available_memory_gb=available_memory_gb,
                disk_io_speed=disk_io_speed,
                network_bandwidth=network_bandwidth,
                current_load=cpu_percent,
                recommended_concurrency=recommended_concurrency,
                recommended_cache_size=recommended_cache_size,
                recommended_thread_pool_size=recommended_thread_pool_size
            )

            self.current_profile = profile
            self.performance_history.append({
                "timestamp": datetime.now(),
                "profile": profile
            })

            # Ограничиваем историю последними 100 записями
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]

            return profile

        except Exception as e:
            self.log_activity(f"Ошибка анализа производительности: {e}", "error")
            return None

    def generate_optimized_config(self, profile: PerformanceProfile) -> OptimizedConfig:
        """Генерация оптимизированной конфигурации на основе профиля"""
        if not profile:
            return self._get_default_config()

        # Базовые значения
        base_concurrency = profile.recommended_concurrency
        base_cache_size = profile.recommended_cache_size
        base_thread_pool = profile.recommended_thread_pool_size

        # Применение правил оптимизации
        cpu_level = self._get_cpu_level(profile.current_load)
        memory_level = self._get_memory_level(profile.available_memory_gb / profile.total_memory_gb * 100)
        network_level = self._get_network_level(profile.network_bandwidth)

        # Оптимизация concurrency
        concurrency_multiplier = self.optimization_rules["cpu_optimization"]["concurrency_multipliers"][cpu_level]
        optimized_concurrency = max(1, int(base_concurrency * concurrency_multiplier))

        # Оптимизация кэша
        cache_multiplier = self.optimization_rules["memory_optimization"]["cache_size_multipliers"][memory_level]
        max(100, int(base_cache_size * cache_multiplier))

        # Оптимизация таймаутов
        timeout_multiplier = self.optimization_rules["network_optimization"]["timeout_multipliers"][network_level]
        base_timeout = 300
        optimized_timeout = int(base_timeout * timeout_multiplier)

        # Генерация конфигурации
        config = OptimizedConfig(
            # SFM параметры
            max_concurrent_functions=optimized_concurrency,
            function_timeout=optimized_timeout,
            cache_ttl=3600,
            sleep_check_interval=300,
            max_thread_pool_workers=base_thread_pool,

            # Scaling параметры
            max_instances=min(profile.cpu_cores * 4, 100),
            min_instances=1,
            cpu_threshold=80.0,
            memory_threshold=85.0,
            scale_up_cooldown=60,
            scale_down_cooldown=300,

            # Load Balancer параметры
            health_check_interval=30,
            max_retries=3,
            timeout=optimized_timeout,

            # Circuit Breaker параметры
            failure_threshold=5,
            success_threshold=3,
            recovery_timeout=60,

            # Zero Trust параметры
            trust_verification_timeout=10,
            max_concurrent_verifications=base_concurrency
        )

        self.optimized_config = config
        return config

    def _get_cpu_level(self, cpu_percent: float) -> str:
        """Определение уровня загрузки CPU"""
        if cpu_percent >= self.optimization_rules["cpu_optimization"]["high_cpu_threshold"]:
            return "high"
        elif cpu_percent >= self.optimization_rules["cpu_optimization"]["medium_cpu_threshold"]:
            return "medium"
        else:
            return "low"

    def _get_memory_level(self, memory_percent: float) -> str:
        """Определение уровня использования памяти"""
        if memory_percent >= self.optimization_rules["memory_optimization"]["high_memory_threshold"]:
            return "high"
        elif memory_percent >= self.optimization_rules["memory_optimization"]["medium_memory_threshold"]:
            return "medium"
        else:
            return "low"

    def _get_network_level(self, bandwidth: float) -> str:
        """Определение уровня сетевой производительности"""
        if bandwidth >= self.optimization_rules["network_optimization"]["high_bandwidth_threshold"]:
            return "high"
        elif bandwidth >= self.optimization_rules["network_optimization"]["medium_bandwidth_threshold"]:
            return "medium"
        else:
            return "low"

    def _get_default_config(self) -> OptimizedConfig:
        """Получение конфигурации по умолчанию"""
        return OptimizedConfig(
            max_concurrent_functions=50,
            function_timeout=300,
            cache_ttl=3600,
            sleep_check_interval=3600,
            max_thread_pool_workers=10,
            max_instances=20,
            min_instances=1,
            cpu_threshold=80.0,
            memory_threshold=85.0,
            scale_up_cooldown=300,
            scale_down_cooldown=600,
            health_check_interval=30,
            max_retries=3,
            timeout=300,
            failure_threshold=5,
            success_threshold=3,
            recovery_timeout=60,
            trust_verification_timeout=10,
            max_concurrent_verifications=50
        )

    async def start_monitoring(self):
        """Запуск мониторинга производительности"""
        self.monitoring_active = True
        self.log_activity("Запуск мониторинга производительности")

        while self.monitoring_active:
            try:
                profile = await self.analyze_system_performance()
                if profile:
                    config = self.generate_optimized_config(profile)
                    await self._apply_optimizations(config)

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                self.log_activity(f"Ошибка мониторинга: {e}", "error")
                await asyncio.sleep(60)  # Пауза при ошибке

    async def stop_monitoring(self):
        """Остановка мониторинга производительности"""
        self.monitoring_active = False
        self.log_activity("Остановка мониторинга производительности")

    async def _apply_optimizations(self, config: OptimizedConfig):
        """Применение оптимизаций к системе"""
        try:
            # Здесь должна быть логика применения конфигурации
            # к реальным компонентам системы

            self.log_activity(f"Применение оптимизаций: concurrency={config.max_concurrent_functions}, "
                              f"cache_size={config.cache_ttl}, threads={config.max_thread_pool_workers}")

            # Сохранение конфигурации
            await self._save_optimized_config(config)

        except Exception as e:
            self.log_activity(f"Ошибка применения оптимизаций: {e}", "error")

    async def _save_optimized_config(self, config: OptimizedConfig):
        """Сохранение оптимизированной конфигурации"""
        try:
            config_data = {
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "max_concurrent_functions": config.max_concurrent_functions,
                    "function_timeout": config.function_timeout,
                    "cache_ttl": config.cache_ttl,
                    "sleep_check_interval": config.sleep_check_interval,
                    "max_thread_pool_workers": config.max_thread_pool_workers,
                    "max_instances": config.max_instances,
                    "min_instances": config.min_instances,
                    "cpu_threshold": config.cpu_threshold,
                    "memory_threshold": config.memory_threshold,
                    "scale_up_cooldown": config.scale_up_cooldown,
                    "scale_down_cooldown": config.scale_down_cooldown,
                    "health_check_interval": config.health_check_interval,
                    "max_retries": config.max_retries,
                    "timeout": config.timeout,
                    "failure_threshold": config.failure_threshold,
                    "success_threshold": config.success_threshold,
                    "recovery_timeout": config.recovery_timeout,
                    "trust_verification_timeout": config.trust_verification_timeout,
                    "max_concurrent_verifications": config.max_concurrent_verifications
                }
            }

            with open("data/optimized_config.json", "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_activity(f"Ошибка сохранения конфигурации: {e}", "error")

    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        if not self.performance_history:
            return {"status": "no_data", "message": "Нет данных о производительности"}

        latest_profile = self.performance_history[-1]["profile"]

        return {
            "current_profile": {
                "cpu_cores": latest_profile.cpu_cores,
                "total_memory_gb": latest_profile.total_memory_gb,
                "available_memory_gb": latest_profile.available_memory_gb,
                "current_load": latest_profile.current_load,
                "recommended_concurrency": latest_profile.recommended_concurrency,
                "recommended_cache_size": latest_profile.recommended_cache_size,
                "recommended_thread_pool_size": latest_profile.recommended_thread_pool_size
            },
            "optimized_config": self.optimized_config.__dict__ if self.optimized_config else None,
            "history_count": len(self.performance_history),
            "monitoring_active": self.monitoring_active
        }


# Пример использования
async def main():
    """Пример использования Performance Optimizer"""
    optimizer = PerformanceOptimizer()

    # Анализ производительности
    profile = await optimizer.analyze_system_performance()
    if profile:
        print(f"✅ Профиль производительности: {profile}")

        # Генерация оптимизированной конфигурации
        config = optimizer.generate_optimized_config(profile)
        print(f"✅ Оптимизированная конфигурация: {config}")

        # Запуск мониторинга
        await optimizer.start_monitoring()

        # Ожидание 5 минут
        await asyncio.sleep(300)

        # Остановка мониторинга
        await optimizer.stop_monitoring()

        # Получение отчета
        report = optimizer.get_performance_report()
        print(f"✅ Отчет о производительности: {report}")
    else:
        print("❌ Ошибка анализа производительности")


if __name__ == "__main__":
    asyncio.run(main())
