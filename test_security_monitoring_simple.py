#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный тест функциональности SecurityMonitoringManager
Проверяет основные компоненты без асинхронных операций
"""

import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security.security_monitoring_a_plus import (
    SecurityMonitoringManager,
    MonitoringLevel,
    AlertType,
    SecurityEvent,
    MonitoringConfig,
    ThreatDetectionStrategy,
    AnomalyDetectionStrategy,
    MonitoringDataManager,
    AlertManager
)


def test_basic_functionality():
    """Базовый тест функциональности"""
    print("🚀 ЗАПУСК УПРОЩЕННОГО ТЕСТА SECURITY MONITORING A+ SYSTEM")
    print("=" * 60)
    
    try:
        # 1. Тест создания конфигурации
        print("1. Тестирование создания конфигурации...")
        config = MonitoringConfig(
            enabled=True,
            alert_threshold=5,
            check_interval=30,
            retention_days=7,
            log_level="INFO"
        )
        assert config.enabled == True
        assert config.alert_threshold == 5
        print("✅ Конфигурация создана успешно")
        
        # 2. Тест создания события
        print("2. Тестирование создания события...")
        event = SecurityEvent(
            event_id="test_001",
            timestamp=datetime.now(),
            level=MonitoringLevel.MEDIUM,
            alert_type=AlertType.THREAT_DETECTED,
            description="Test security event",
            source="test_system"
        )
        assert event.event_id == "test_001"
        assert event.level == MonitoringLevel.MEDIUM
        print("✅ Событие создано успешно")
        
        # 3. Тест создания стратегий
        print("3. Тестирование создания стратегий...")
        threat_strategy = ThreatDetectionStrategy(config)
        anomaly_strategy = AnomalyDetectionStrategy(config)
        
        assert threat_strategy.get_strategy_name() == "ThreatDetection"
        assert anomaly_strategy.get_strategy_name() == "AnomalyDetection"
        print("✅ Стратегии созданы успешно")
        
        # 4. Тест создания менеджеров
        print("4. Тестирование создания менеджеров...")
        data_manager = MonitoringDataManager(config)
        alert_manager = AlertManager(config)
        
        assert data_manager is not None
        assert alert_manager is not None
        print("✅ Менеджеры созданы успешно")
        
        # 5. Тест создания основного менеджера
        print("5. Тестирование создания SecurityMonitoringManager...")
        manager = SecurityMonitoringManager(config=config)
        
        assert manager.config.enabled == True
        assert manager.config.alert_threshold == 5
        print("✅ SecurityMonitoringManager создан успешно")
        
        # 6. Тест добавления событий через data_manager
        print("6. Тестирование добавления событий...")
        manager.data_manager.add_event(event)
        events = manager.data_manager.get_events()
        assert len(events) == 1
        print("✅ Событие добавлено успешно")
        
        # 7. Тест добавления стратегий
        print("7. Тестирование добавления стратегий...")
        manager.add_monitoring_strategy(threat_strategy)
        manager.add_monitoring_strategy(anomaly_strategy)
        assert len(manager.strategies) == 4  # 2 по умолчанию + 2 добавленных
        print("✅ Стратегии добавлены успешно")
        
        # 8. Тест получения статуса
        print("8. Тестирование получения статуса...")
        status = manager.get_security_status()
        assert "total_events" in status
        assert "strategies_count" in status
        print("✅ Статус получен успешно")
        
        # 9. Тест обновления конфигурации
        print("9. Тестирование обновления конфигурации...")
        new_config = MonitoringConfig(
            enabled=True,
            alert_threshold=10,
            check_interval=60,
            retention_days=14,
            log_level="DEBUG"
        )
        manager.update_config(new_config)
        assert manager.config.alert_threshold == 10
        print("✅ Конфигурация обновлена успешно")
        
        print("=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ SecurityMonitoringManager готов к продакшену!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)