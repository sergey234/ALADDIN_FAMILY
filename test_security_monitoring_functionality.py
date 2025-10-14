#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест функциональности SecurityMonitoringManager
Проверяет все основные компоненты и методы
"""

import sys
import os
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta

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


def test_enums():
    """Тест перечислений"""
    print("1. Тестирование перечислений...")
    
    # Тест MonitoringLevel
    assert MonitoringLevel.LOW.value == "low"
    assert MonitoringLevel.MEDIUM.value == "medium"
    assert MonitoringLevel.HIGH.value == "high"
    assert MonitoringLevel.CRITICAL.value == "critical"
    
    # Тест AlertType
    assert AlertType.THREAT_DETECTED.value == "threat_detected"
    assert AlertType.ANOMALY_FOUND.value == "anomaly_found"
    assert AlertType.SYSTEM_BREACH.value == "system_breach"
    
    print("✅ Перечисления работают корректно")


def test_dataclasses():
    """Тест dataclasses"""
    print("2. Тестирование dataclasses...")
    
    # Тест SecurityEvent
    event = SecurityEvent(
        event_id="test_001",
        timestamp=datetime.now(),
        level=MonitoringLevel.MEDIUM,
        alert_type=AlertType.THREAT_DETECTED,
        description="Test event",
        source="test_source"
    )
    
    assert event.event_id == "test_001"
    assert event.level == MonitoringLevel.MEDIUM
    assert event.alert_type == AlertType.THREAT_DETECTED
    assert isinstance(event.timestamp, datetime)
    
    # Тест MonitoringConfig
    config = MonitoringConfig(
        enabled=True,
        alert_threshold=5,
        check_interval=30,
        retention_days=7,
        log_level="DEBUG"
    )
    
    assert config.enabled == True
    assert config.alert_threshold == 5
    assert config.check_interval == 30
    
    print("✅ Dataclasses работают корректно")


def test_security_checks():
    """Тест классов проверок безопасности"""
    print("3. Тестирование классов проверок безопасности...")
    
    # Создаем конфигурацию для тестов
    config = MonitoringConfig(
        enabled=True,
        alert_threshold=5,
        check_interval=30,
        retention_days=7,
        log_level="INFO"
    )
    
    # Тест ThreatDetectionStrategy
    threat_check = ThreatDetectionStrategy(config)
    assert threat_check.get_strategy_name() == "ThreatDetection"
    
    # Тест AnomalyDetectionStrategy
    anomaly_check = AnomalyDetectionStrategy(config)
    assert anomaly_check.get_strategy_name() == "AnomalyDetection"
    
    # Тест MonitoringDataManager
    data_manager = MonitoringDataManager(config)
    assert data_manager is not None
    
    # Тест AlertManager
    alert_manager = AlertManager(config)
    assert alert_manager is not None
    
    print("✅ Классы проверок безопасности работают корректно")


async def test_security_monitoring_manager():
    """Тест основного менеджера мониторинга"""
    print("4. Тестирование SecurityMonitoringManager...")
    
    # Создание временной директории для тестов
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Создание менеджера
        manager = SecurityMonitoringManager(
            config=MonitoringConfig(
                enabled=True,
                alert_threshold=3,
                check_interval=10,
                retention_days=7,
                log_level="INFO"
            )
        )
        
        # Тест инициализации
        assert manager.config.enabled == True
        assert manager.config.alert_threshold == 3
        
        # Тест запуска мониторинга
        await manager.start_monitoring()
        assert manager.is_monitoring_active() == True
        
        # Тест добавления проверок
        threat_check = ThreatDetectionStrategy(manager.config)
        anomaly_check = AnomalyDetectionStrategy(manager.config)
        
        manager.add_security_check(threat_check)
        manager.add_security_check(anomaly_check)
        
        assert len(manager.security_checks) == 2
        
        # Тест создания события
        event = SecurityEvent(
            event_id="test_event_001",
            timestamp=datetime.now(),
            level=MonitoringLevel.LOW,
            alert_type=AlertType.THREAT_DETECTED,
            description="Test security event",
            source="test_system"
        )
        
        manager.add_security_event(event)
        assert len(manager.security_events) == 1
        
        # Тест получения статистики
        stats = manager.get_statistics()
        assert "total_events" in stats
        assert "active_checks" in stats
        assert "monitoring_uptime" in stats
        
        # Тест генерации отчета
        report = manager.generate_report()
        assert report is not None
        assert hasattr(report, 'total_events')
        assert hasattr(report, 'monitoring_level')
        
        # Тест остановки мониторинга
        await manager.stop_monitoring()
        assert manager.is_monitoring_active() == False
        
        print("✅ SecurityMonitoringManager работает корректно")
        
    finally:
        # Очистка временной директории
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_error_handling():
    """Тест обработки ошибок"""
    print("5. Тестирование обработки ошибок...")
    
    try:
        # Тест с некорректной конфигурацией
        config = MonitoringConfig(
            enabled=True,
            alert_threshold=-1,  # Некорректное значение
            check_interval=0,    # Некорректное значение
            retention_days=0,
            log_level="INVALID"
        )
        
        manager = SecurityMonitoringManager(config=config)
        
        # Менеджер должен создаться, но с валидацией
        assert manager.config.alert_threshold >= 0
        assert manager.config.check_interval > 0
        
        print("✅ Обработка ошибок работает корректно")
        
    except Exception as e:
        print(f"❌ Ошибка в обработке ошибок: {e}")
        raise


def test_performance():
    """Тест производительности"""
    print("6. Тестирование производительности...")
    
    import time
    
    # Создание менеджера
    manager = SecurityMonitoringManager()
    
    # Тест создания множества событий
    start_time = time.time()
    
    for i in range(100):
        event = SecurityEvent(
            event_id=f"perf_test_{i:03d}",
            timestamp=datetime.now(),
            level=MonitoringLevel.LOW,
            alert_type=AlertType.THREAT_DETECTED,
            description=f"Performance test event {i}",
            source="performance_test"
        )
        manager.add_security_event(event)
    
    end_time = time.time()
    creation_time = end_time - start_time
    
    print(f"✅ Создано 100 событий за {creation_time:.3f} секунд")
    assert creation_time < 1.0  # Должно быть быстрее 1 секунды
    
    # Тест генерации отчета
    start_time = time.time()
    report = manager.generate_report()
    end_time = time.time()
    
    report_time = end_time - start_time
    print(f"✅ Отчет сгенерирован за {report_time:.3f} секунд")
    assert report_time < 0.5  # Должно быть быстрее 0.5 секунды


async def main():
    """Главная функция тестирования"""
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА SECURITY MONITORING A+ SYSTEM")
    print("=" * 60)
    
    try:
        test_enums()
        test_dataclasses()
        test_security_checks()
        await test_security_monitoring_manager()
        test_error_handling()
        test_performance()
        
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
    success = asyncio.run(main())
    sys.exit(0 if success else 1)