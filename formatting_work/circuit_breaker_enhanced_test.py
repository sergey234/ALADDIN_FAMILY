#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест улучшенных методов Circuit Breaker Main
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

def test_circuit_state_enhanced():
    """Тест улучшенных методов CircuitState"""
    print("🔍 Тестирование улучшенных методов CircuitState...")
    
    # Тест __str__
    assert str(CircuitState.CLOSED) == "CircuitState.CLOSED"
    assert str(CircuitState.OPEN) == "CircuitState.OPEN"
    assert str(CircuitState.HALF_OPEN) == "CircuitState.HALF_OPEN"
    
    # Тест __repr__
    assert repr(CircuitState.CLOSED) == "CircuitState.CLOSED"
    
    # Тест __bool__
    assert bool(CircuitState.CLOSED) == True
    assert bool(CircuitState.OPEN) == False
    assert bool(CircuitState.HALF_OPEN) == True
    
    # Тест новых методов
    assert CircuitState.CLOSED.is_closed() == True
    assert CircuitState.OPEN.is_open() == True
    assert CircuitState.HALF_OPEN.is_half_open() == True
    
    assert CircuitState.CLOSED.can_accept_calls() == True
    assert CircuitState.OPEN.can_accept_calls() == False
    assert CircuitState.HALF_OPEN.can_accept_calls() == True
    
    # Тест описаний
    assert "нормальная работа" in CircuitState.CLOSED.get_description()
    assert "блокировка вызовов" in CircuitState.OPEN.get_description()
    assert "тестирование" in CircuitState.HALF_OPEN.get_description()
    
    print("✅ Улучшенные методы CircuitState работают корректно")

def test_circuit_breaker_config_enhanced():
    """Тест улучшенных методов CircuitBreakerConfig"""
    print("🔍 Тестирование улучшенных методов CircuitBreakerConfig...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=5,
        timeout=60
    )
    
    # Тест __str__
    str_repr = str(config)
    assert "test_service" in str_repr
    assert "api" in str_repr
    assert "standard" in str_repr
    
    # Тест __repr__
    repr_str = repr(config)
    assert "CircuitBreakerConfig" in repr_str
    assert "test_service" in repr_str
    
    # Тест __bool__
    assert bool(config) == True
    
    # Тест валидации
    assert config.validate() == True
    
    # Тест to_dict
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict["service_name"] == "test_service"
    assert config_dict["service_type"] == "api"
    
    # Тест from_dict
    new_config = CircuitBreakerConfig.from_dict(config_dict)
    assert new_config.service_name == config.service_name
    assert new_config.service_type == config.service_type
    
    # Тест __hash__
    config_hash = hash(config)
    assert isinstance(config_hash, int)
    
    # Тест невалидной конфигурации
    invalid_config = CircuitBreakerConfig(
        service_name="",
        service_type="api",
        strategy="standard",
        failure_threshold=5,
        timeout=60
    )
    assert bool(invalid_config) == False
    assert invalid_config.validate() == False
    
    print("✅ Улучшенные методы CircuitBreakerConfig работают корректно")

def test_circuit_breaker_main_enhanced():
    """Тест улучшенных методов CircuitBreakerMain"""
    print("🔍 Тестирование улучшенных методов CircuitBreakerMain...")
    
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
    
    # Тест __str__
    str_repr = str(circuit_breaker)
    assert "test_service" in str_repr
    assert "closed" in str_repr  # Используем значение, а не имя
    
    # Тест __repr__
    repr_str = repr(circuit_breaker)
    assert "CircuitBreakerMain" in repr_str
    assert "test_service" in repr_str
    
    # Тест __bool__
    assert bool(circuit_breaker) == True
    
    # Тест __len__
    assert len(circuit_breaker) == 0  # Изначально 0 вызовов
    
    # Тест __iter__
    stats_items = list(circuit_breaker)
    assert isinstance(stats_items, list)
    assert len(stats_items) > 0
    
    # Тест __contains__
    assert "total_calls" in circuit_breaker
    assert "successful_calls" in circuit_breaker
    assert "nonexistent" not in circuit_breaker
    
    # Тест __getitem__ и __setitem__
    circuit_breaker["test_key"] = "test_value"
    assert circuit_breaker["test_key"] == "test_value"
    
    # Тест __delitem__
    del circuit_breaker["test_key"]
    assert "test_key" not in circuit_breaker
    
    # Тест __eq__
    same_config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=3,
        timeout=30
    )
    same_circuit_breaker = CircuitBreakerMain(same_config)
    assert circuit_breaker == same_circuit_breaker
    
    # Тест __hash__
    circuit_breaker_hash = hash(circuit_breaker)
    assert isinstance(circuit_breaker_hash, int)
    
    print("✅ Улучшенные методы CircuitBreakerMain работают корректно")

def test_context_manager():
    """Тест контекстного менеджера"""
    print("🔍 Тестирование контекстного менеджера...")
    
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
    
    # Тест успешного выполнения в контексте
    with circuit_breaker as cb:
        assert cb == circuit_breaker
        result = cb.call(lambda x, y: x + y, 5, 3)
        assert result == 8
    
    # Тест обработки исключений в контексте
    try:
        with circuit_breaker as cb:
            def failing_func():
                raise Exception("Test error")
            cb.call(failing_func)
    except Exception as e:
        assert str(e) == "Test error"
    
    print("✅ Контекстный менеджер работает корректно")

def test_enhanced_functionality():
    """Тест расширенной функциональности"""
    print("🔍 Тестирование расширенной функциональности...")
    
    # Создаем конфигурацию
    config = CircuitBreakerConfig(
        service_name="test_service",
        service_type="api",
        strategy="standard",
        failure_threshold=2,
        timeout=1
    )
    
    # Создаем экземпляр
    circuit_breaker = CircuitBreakerMain(config)
    
    # Тест итерации по статистике
    for key, value in circuit_breaker:
        assert isinstance(key, str)
        assert isinstance(value, (int, float))
    
    # Тест словарного доступа к статистике
    circuit_breaker["custom_metric"] = 100
    assert circuit_breaker["custom_metric"] == 100
    
    # Тест булевого представления
    assert bool(circuit_breaker) == True
    
    # Тест длины (количество вызовов)
    assert len(circuit_breaker) == 0
    
    # Делаем несколько вызовов
    circuit_breaker.call(lambda: "success")
    circuit_breaker.call(lambda: "success")
    
    assert len(circuit_breaker) == 2
    
    print("✅ Расширенная функциональность работает корректно")

def run_enhanced_tests():
    """Запуск всех улучшенных тестов"""
    print("🚀 ЗАПУСК УЛУЧШЕННЫХ ТЕСТОВ CIRCUIT BREAKER MAIN")
    print("=" * 60)
    
    try:
        test_circuit_state_enhanced()
        test_circuit_breaker_config_enhanced()
        test_circuit_breaker_main_enhanced()
        test_context_manager()
        test_enhanced_functionality()
        
        print("\n🎉 ВСЕ УЛУЧШЕННЫЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Circuit Breaker Main с улучшениями полностью функционален")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В УЛУЧШЕННЫХ ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_enhanced_tests()
    
    if success:
        print("\n🏆 ВСЕ УЛУЧШЕНИЯ РАБОТАЮТ КОРРЕКТНО!")
        print("✅ Circuit Breaker Main готов к использованию с улучшениями")
    else:
        print("\n💥 НЕКОТОРЫЕ УЛУЧШЕНИЯ НЕ РАБОТАЮТ!")
        print("❌ Требуется исправление")