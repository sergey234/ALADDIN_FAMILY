#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест улучшений SecurityMonitoringManager
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
    SecurityMonitoringManager
)


def test_special_methods():
    """Тест специальных методов"""
    print("🚀 ТЕСТ СПЕЦИАЛЬНЫХ МЕТОДОВ")
    print("=" * 50)
    
    try:
        # 1. Тест SecurityEvent
        print("1. Тестирование SecurityEvent...")
        event1 = SecurityEvent(
            event_id="test_001",
            timestamp=datetime.now(),
            level=MonitoringLevel.HIGH,
            alert_type=AlertType.THREAT_DETECTED,
            description="Test event",
            source="test_system"
        )
        
        event2 = SecurityEvent(
            event_id="test_002",
            timestamp=datetime.now(),
            level=MonitoringLevel.MEDIUM,
            alert_type=AlertType.ANOMALY_FOUND,
            description="Test event 2",
            source="test_system"
        )
        
        # Тест __str__
        print(f"✅ __str__: {str(event1)}")
        
        # Тест __repr__
        print(f"✅ __repr__: {repr(event1)}")
        
        # Тест __eq__
        assert event1 != event2, "События должны быть разными"
        assert event1 == event1, "Событие должно быть равно самому себе"
        print("✅ __eq__ работает корректно")
        
        # 2. Тест MonitoringConfig
        print("\n2. Тестирование MonitoringConfig...")
        config1 = MonitoringConfig(
            enabled=True,
            alert_threshold=5,
            check_interval=30,
            retention_days=7,
            log_level="INFO"
        )
        
        config2 = MonitoringConfig(
            enabled=False,
            alert_threshold=10,
            check_interval=60,
            retention_days=14,
            log_level="DEBUG"
        )
        
        # Тест __str__
        print(f"✅ __str__: {str(config1)}")
        
        # Тест __repr__
        print(f"✅ __repr__: {repr(config1)}")
        
        # Тест __eq__
        assert config1 != config2, "Конфигурации должны быть разными"
        assert config1 == config1, "Конфигурация должна быть равна самой себе"
        print("✅ __eq__ работает корректно")
        
        # 3. Тест SecurityMonitoringManager
        print("\n3. Тестирование SecurityMonitoringManager...")
        manager = SecurityMonitoringManager(
            name="TestManager",
            config=config1
        )
        
        # Тест __str__
        print(f"✅ __str__: {str(manager)}")
        
        # Тест __repr__
        print(f"✅ __repr__: {repr(manager)}")
        
        # Тест __len__
        print(f"✅ __len__: {len(manager)} стратегий")
        
        # Тест __iter__
        strategies = list(manager)
        print(f"✅ __iter__: {len(strategies)} стратегий в итерации")
        
        # Тест __contains__
        threat_strategy = ThreatDetectionStrategy(config1)
        manager.add_monitoring_strategy(threat_strategy)
        assert threat_strategy in manager, "Стратегия должна быть в менеджере"
        print("✅ __contains__ работает корректно")
        
        # Тест __enter__ и __exit__
        print("\n4. Тестирование контекстного менеджера...")
        with manager as m:
            assert m is manager, "Контекстный менеджер должен возвращать self"
            print("✅ __enter__ работает корректно")
        print("✅ __exit__ работает корректно")
        
        # 5. Тест property методов
        print("\n5. Тестирование property методов...")
        print(f"✅ is_running: {manager.is_running}")
        print(f"✅ strategies_count: {manager.strategies_count}")
        print(f"✅ status_info: {len(manager.status_info)} полей")
        
        # 6. Тест static методов
        print("\n6. Тестирование static методов...")
        levels = SecurityMonitoringManager.get_supported_levels()
        alert_types = SecurityMonitoringManager.get_supported_alert_types()
        print(f"✅ get_supported_levels: {len(levels)} уровней")
        print(f"✅ get_supported_alert_types: {len(alert_types)} типов")
        
        # 7. Тест class метода
        print("\n7. Тестирование class метода...")
        custom_manager = SecurityMonitoringManager.create_with_custom_config(
            "CustomManager", config2
        )
        assert custom_manager.name == "CustomManager", "Имя должно быть CustomManager"
        assert custom_manager.config == config2, "Конфигурация должна совпадать"
        print("✅ create_with_custom_config работает корректно")
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ СПЕЦИАЛЬНЫЕ МЕТОДЫ РАБОТАЮТ!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В ТЕСТЕ СПЕЦИАЛЬНЫХ МЕТОДОВ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_special_methods()
    sys.exit(0 if success else 1)