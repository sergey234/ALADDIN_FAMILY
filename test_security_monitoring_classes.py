#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания экземпляров всех классов SecurityMonitoringManager
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


def test_class_instantiation():
    """Тест создания экземпляров всех классов"""
    print("🚀 ТЕСТ СОЗДАНИЯ ЭКЗЕМПЛЯРОВ КЛАССОВ")
    print("=" * 50)
    
    try:
        # 1. Тест перечислений
        print("1. Тестирование перечислений...")
        monitoring_level = MonitoringLevel.HIGH
        alert_type = AlertType.THREAT_DETECTED
        print(f"✅ MonitoringLevel: {monitoring_level}")
        print(f"✅ AlertType: {alert_type}")
        
        # 2. Тест dataclasses
        print("\n2. Тестирование dataclasses...")
        security_event = SecurityEvent(
            event_id="test_001",
            timestamp=datetime.now(),
            level=MonitoringLevel.MEDIUM,
            alert_type=AlertType.THREAT_DETECTED,
            description="Test event",
            source="test_system"
        )
        print(f"✅ SecurityEvent: {security_event.event_id}")
        
        monitoring_config = MonitoringConfig(
            enabled=True,
            alert_threshold=5,
            check_interval=30,
            retention_days=7,
            log_level="INFO"
        )
        print(f"✅ MonitoringConfig: {monitoring_config.enabled}")
        
        # 3. Тест стратегий
        print("\n3. Тестирование стратегий...")
        threat_strategy = ThreatDetectionStrategy(monitoring_config)
        anomaly_strategy = AnomalyDetectionStrategy(monitoring_config)
        print(f"✅ ThreatDetectionStrategy: {threat_strategy.get_strategy_name()}")
        print(f"✅ AnomalyDetectionStrategy: {anomaly_strategy.get_strategy_name()}")
        
        # 4. Тест менеджеров
        print("\n4. Тестирование менеджеров...")
        data_manager = MonitoringDataManager(monitoring_config)
        alert_manager = AlertManager(monitoring_config)
        print(f"✅ MonitoringDataManager: {type(data_manager).__name__}")
        print(f"✅ AlertManager: {type(alert_manager).__name__}")
        
        # 5. Тест основного менеджера
        print("\n5. Тестирование SecurityMonitoringManager...")
        main_manager = SecurityMonitoringManager(
            name="TestManager",
            config=monitoring_config
        )
        print(f"✅ SecurityMonitoringManager: {main_manager.name}")
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ КЛАССЫ СОЗДАНЫ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА ПРИ СОЗДАНИИ КЛАССОВ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_class_instantiation()
    sys.exit(0 if success else 1)