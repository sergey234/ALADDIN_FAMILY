#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест доступности всех public методов SecurityMonitoringManager
"""

import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security.security_monitoring_a_plus import (
    MonitoringLevel,
    AlertType,
    SecurityEvent,
    MonitoringConfig,
    ThreatDetectionStrategy,
    AnomalyDetectionStrategy,
    MonitoringDataManager,
    AlertManager,
    SecurityMonitoringManager
)


def test_public_methods():
    """Тест доступности всех public методов"""
    print("🚀 ТЕСТ ДОСТУПНОСТИ PUBLIC МЕТОДОВ")
    print("=" * 50)
    
    try:
        # Создаем конфигурацию
        config = MonitoringConfig(
            enabled=True,
            alert_threshold=5,
            check_interval=30,
            retention_days=7,
            log_level="INFO"
        )
        
        # 1. Тест методов ThreatDetectionStrategy
        print("1. Тестирование ThreatDetectionStrategy...")
        threat_strategy = ThreatDetectionStrategy(config)
        
        # Проверяем доступность методов
        assert hasattr(threat_strategy, 'check_security'), "check_security не найден"
        assert hasattr(threat_strategy, 'get_strategy_name'), "get_strategy_name не найден"
        
        # Тестируем методы
        strategy_name = threat_strategy.get_strategy_name()
        assert strategy_name == "ThreatDetection", f"Неверное имя стратегии: {strategy_name}"
        print(f"✅ ThreatDetectionStrategy: {strategy_name}")
        
        # 2. Тест методов AnomalyDetectionStrategy
        print("2. Тестирование AnomalyDetectionStrategy...")
        anomaly_strategy = AnomalyDetectionStrategy(config)
        
        strategy_name = anomaly_strategy.get_strategy_name()
        assert strategy_name == "AnomalyDetection", f"Неверное имя стратегии: {strategy_name}"
        print(f"✅ AnomalyDetectionStrategy: {strategy_name}")
        
        # 3. Тест методов MonitoringDataManager
        print("3. Тестирование MonitoringDataManager...")
        data_manager = MonitoringDataManager(config)
        
        # Проверяем доступность методов
        assert hasattr(data_manager, 'add_event'), "add_event не найден"
        assert hasattr(data_manager, 'get_events'), "get_events не найден"
        assert hasattr(data_manager, 'get_events_by_level'), "get_events_by_level не найден"
        
        # Тестируем методы
        events = data_manager.get_events()
        assert isinstance(events, list), "get_events должен возвращать список"
        print(f"✅ MonitoringDataManager: {len(events)} событий")
        
        # 4. Тест методов AlertManager
        print("4. Тестирование AlertManager...")
        alert_manager = AlertManager(config)
        
        # Проверяем доступность методов
        assert hasattr(alert_manager, 'process_events'), "process_events не найден"
        
        print(f"✅ AlertManager: {type(alert_manager).__name__}")
        
        # 5. Тест методов SecurityMonitoringManager
        print("5. Тестирование SecurityMonitoringManager...")
        main_manager = SecurityMonitoringManager(
            name="TestManager",
            config=config
        )
        
        # Проверяем доступность методов
        assert hasattr(main_manager, 'add_monitoring_strategy'), "add_monitoring_strategy не найден"
        assert hasattr(main_manager, 'remove_monitoring_strategy'), "remove_monitoring_strategy не найден"
        assert hasattr(main_manager, 'get_security_status'), "get_security_status не найден"
        assert hasattr(main_manager, 'update_config'), "update_config не найден"
        assert hasattr(main_manager, 'stop_monitoring'), "stop_monitoring не найден"
        
        # Тестируем методы
        status = main_manager.get_security_status()
        assert isinstance(status, dict), "get_security_status должен возвращать словарь"
        assert "total_events" in status, "status должен содержать total_events"
        print(f"✅ SecurityMonitoringManager: {len(status)} полей статуса")
        
        # 6. Тест добавления стратегий
        print("6. Тестирование добавления стратегий...")
        main_manager.add_monitoring_strategy(threat_strategy)
        main_manager.add_monitoring_strategy(anomaly_strategy)
        
        # Проверяем что стратегии добавлены
        assert len(main_manager.strategies) >= 2, "Стратегии не добавлены"
        print(f"✅ Добавлено стратегий: {len(main_manager.strategies)}")
        
        # 7. Тест обновления конфигурации
        print("7. Тестирование обновления конфигурации...")
        new_config = MonitoringConfig(
            enabled=True,
            alert_threshold=10,
            check_interval=60,
            retention_days=14,
            log_level="DEBUG"
        )
        main_manager.update_config(new_config)
        
        assert main_manager.config.alert_threshold == 10, "Конфигурация не обновлена"
        print(f"✅ Конфигурация обновлена: threshold={main_manager.config.alert_threshold}")
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ PUBLIC МЕТОДЫ ДОСТУПНЫ!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ МЕТОДОВ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_public_methods()
    sys.exit(0 if success else 1)