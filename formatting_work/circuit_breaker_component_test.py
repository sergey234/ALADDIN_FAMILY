#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест всех компонентов Circuit Breaker Main
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# Добавляем путь к модулю
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.circuit_breaker_main import (
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerMain,
    circuit_breaker_main
)

def test_circuit_state_enum():
    """Тест перечисления CircuitState"""
    print("🔍 Тестирование CircuitState...")
    
    # Проверяем все значения
    assert CircuitState.CLOSED.value == "closed"
    assert CircuitState.OPEN.value == "open"
    assert CircuitState.HALF_OPEN.value == "half_open"
    
    # Проверяем итерацию
    states = list(CircuitState)
    assert len(states) == 3
    
    print("✅ CircuitState работает корректно")

def test_circuit_breaker_config():
    """Тест конфигурации CircuitBreakerConfig"""
    print("🔍 Тестирование CircuitBreakerConfig...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=5,
        timeout=60
    )
    
    # Проверяем атрибуты
    assert config.service_name == "test_service"
    assert config.service_type == "api"
    assert config.strategy == "standard"
    assert config.failure_threshold == 5
    assert config.timeout == 60
    assert config.half_open_max_calls == 5  # значение по умолчанию
    assert config.success_threshold == 3  # значение по умолчанию
    assert config.adaptive == True  # значение по умолчанию
    assert config.ml_enabled == True  # значение по умолчанию
    
    print("✅ CircuitBreakerConfig работает корректно")

def test_circuit_breaker_main_creation():
    """Тест создания CircuitBreakerMain"""
    print("🔍 Тестирование создания CircuitBreakerMain...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=3,
        timeout=30
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Проверяем инициализацию
    assert circuit_breaker.config == config
    assert circuit_breaker.state == CircuitState.CLOSED
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.success_count == 0
    assert circuit_breaker.last_failure_time is None
    assert circuit_breaker.last_success_time is None
    assert circuit_breaker.half_open_calls == 0
    assert isinstance(circuit_breaker.lock, type(circuit_breaker.lock))
    assert isinstance(circuit_breaker.stats, dict)
    
    print("✅ CircuitBreakerMain создается корректно")

def test_circuit_breaker_methods():
    """Тест методов CircuitBreakerMain"""
    print("🔍 Тестирование методов CircuitBreakerMain...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=3,
        timeout=30
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Тест get_state
    state = circuit_breaker.get_state()
    assert isinstance(state, dict)
    assert "service_name" in state
    assert "state" in state
    assert "failure_count" in state
    assert "success_count" in state
    assert "stats" in state
    
    # Тест reset
    circuit_breaker.failure_count = 5
    circuit_breaker.state = CircuitState.OPEN
    circuit_breaker.reset()
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.state == CircuitState.CLOSED
    
    # Тест update_config
    new_config = CircuitBreakerConfig(
        service_name="new_service",
        service_type="database",
        strategy="adaptive",
        failure_threshold=10,
        timeout=120
    )
    circuit_breaker.update_config(new_config)
    assert circuit_breaker.config == new_config
    
    print("✅ Методы CircuitBreakerMain работают корректно")

def test_circuit_breaker_call_success():
    """Тест успешного вызова через Circuit Breaker"""
    print("🔍 Тестирование успешного вызова...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=3,
        timeout=30
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Тестовая функция
    def test_func(x, y):
        return x + y
    
    # Вызываем функцию через Circuit Breaker
    result = circuit_breaker.call(test_func, 5, 3)
    assert result == 8
    
    # Проверяем статистику
    assert circuit_breaker.stats["total_calls"] == 1
    assert circuit_breaker.stats["successful_calls"] == 1
    assert circuit_breaker.stats["failed_calls"] == 0
    
    print("✅ Успешный вызов работает корректно")

def test_circuit_breaker_call_failure():
    """Тест неудачного вызова через Circuit Breaker"""
    print("🔍 Тестирование неудачного вызова...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=2,
        timeout=30
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Тестовая функция, которая всегда падает
    def failing_func():
        raise Exception("Test error")
    
    # Вызываем функцию через Circuit Breaker
    try:
        circuit_breaker.call(failing_func)
        assert False, "Ожидалось исключение"
    except Exception as e:
        assert str(e) == "Test error"
    
    # Проверяем статистику
    assert circuit_breaker.stats["total_calls"] == 1
    assert circuit_breaker.stats["successful_calls"] == 0
    assert circuit_breaker.stats["failed_calls"] == 1
    
    print("✅ Неудачный вызов работает корректно")

def test_circuit_breaker_state_transitions():
    """Тест переходов состояний Circuit Breaker"""
    print("🔍 Тестирование переходов состояний...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=2,
        timeout=1  # Короткий таймаут для тестирования
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Тестовая функция, которая всегда падает
    def failing_func():
        raise Exception("Test error")
    
    # Вызываем функцию несколько раз, чтобы открыть Circuit Breaker
    for i in range(3):
        try:
            circuit_breaker.call(failing_func)
        except Exception:
            pass
    
    # Проверяем, что Circuit Breaker открыт
    assert circuit_breaker.state == CircuitState.OPEN
    # Проверяем, что счетчик открытий увеличился
    assert circuit_breaker.stats["circuit_opens"] >= 1
    
    # Ждем таймаут
    time.sleep(2)
    
    # Тестовая функция, которая работает
    def success_func():
        return "success"
    
    # Вызываем функцию - должна перейти в HALF_OPEN
    result = circuit_breaker.call(success_func)
    assert result == "success"
    assert circuit_breaker.state == CircuitState.HALF_OPEN
    
    print("✅ Переходы состояний работают корректно")

async def test_async_get_status():
    """Тест асинхронного метода get_status"""
    print("🔍 Тестирование async get_status...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=3,
        timeout=30
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Вызываем async метод
    status = await circuit_breaker.get_status()
    
    # Проверяем результат
    assert isinstance(status, dict)
    assert "service_name" in status
    assert "state" in status
    assert "stats" in status
    assert "config" in status
    assert "status" in status
    
    print("✅ Async get_status работает корректно")

def test_global_instance():
    """Тест глобального экземпляра"""
    print("🔍 Тестирование глобального экземпляра...")
    
    # Проверяем, что глобальный экземпляр существует
    assert circuit_breaker_main is not None
    assert isinstance(circuit_breaker_main, CircuitBreakerMain)
    
    # Проверяем его конфигурацию
    assert circuit_breaker_main.config.service_name == "default"
    assert circuit_breaker_main.config.service_type == "api"
    assert circuit_breaker_main.config.strategy == "standard"
    assert circuit_breaker_main.config.failure_threshold == 5
    assert circuit_breaker_main.config.timeout == 60
    
    print("✅ Глобальный экземпляр работает корректно")

def test_cleanup():
    """Тест метода cleanup"""
    print("🔍 Тестирование cleanup...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=3,
        timeout=30
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Изменяем состояние
    circuit_breaker.failure_count = 5
    circuit_breaker.success_count = 3
    circuit_breaker.state = CircuitState.OPEN
    circuit_breaker.stats["total_calls"] = 10
    
    # Вызываем cleanup
    circuit_breaker.cleanup()
    
    # Проверяем, что состояние сброшено
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.success_count == 0
    assert circuit_breaker.state == CircuitState.CLOSED
    assert circuit_breaker.stats["total_calls"] == 0
    
    print("✅ Cleanup работает корректно")

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 ЗАПУСК ВСЕХ ТЕСТОВ CIRCUIT BREAKER MAIN")
    print("=" * 60)
    
    try:
        test_circuit_state_enum()
        test_circuit_breaker_config()
        test_circuit_breaker_main_creation()
        test_circuit_breaker_methods()
        test_circuit_breaker_call_success()
        test_circuit_breaker_call_failure()
        test_circuit_breaker_state_transitions()
        test_global_instance()
        test_cleanup()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Circuit Breaker Main полностью функционален")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_async_tests():
    """Запуск асинхронных тестов"""
    print("\n🔄 ЗАПУСК АСИНХРОННЫХ ТЕСТОВ")
    print("=" * 40)
    
    try:
        await test_async_get_status()
        print("\n🎉 АСИНХРОННЫЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В АСИНХРОННЫХ ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Запускаем синхронные тесты
    sync_success = run_all_tests()
    
    # Запускаем асинхронные тесты
    async_success = asyncio.run(run_async_tests())
    
    # Итоговый результат
    if sync_success and async_success:
        print("\n🏆 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("✅ Circuit Breaker Main готов к использованию")
    else:
        print("\n💥 НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        print("❌ Требуется исправление")