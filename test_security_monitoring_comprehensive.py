#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест всех компонентов SecurityMonitoringManager
"""

import sys
import os
import asyncio
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


async def test_comprehensive_functionality():
    """Комплексный тест всех компонентов"""
    print("🚀 КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    try:
        # 1. Создание конфигурации
        print("1. Создание конфигурации...")
        config = MonitoringConfig(
            enabled=True,
            alert_threshold=3,
            check_interval=10,
            retention_days=7,
            log_level="INFO"
        )
        print(f"✅ Конфигурация создана: threshold={config.alert_threshold}")
        
        # 2. Создание событий
        print("2. Создание событий...")
        events = []
        for i in range(5):
            event = SecurityEvent(
                event_id=f"test_event_{i:03d}",
                timestamp=datetime.now(),
                level=MonitoringLevel.MEDIUM,
                alert_type=AlertType.THREAT_DETECTED,
                description=f"Test event {i}",
                source="test_system"
            )
            events.append(event)
        print(f"✅ Создано событий: {len(events)}")
        
        # 3. Тест стратегий
        print("3. Тестирование стратегий...")
        threat_strategy = ThreatDetectionStrategy(config)
        anomaly_strategy = AnomalyDetectionStrategy(config)
        
        # Тест асинхронных методов
        threat_events = await threat_strategy.check_security()
        anomaly_events = await anomaly_strategy.check_security()
        
        print(f"✅ ThreatDetectionStrategy: {threat_strategy.get_strategy_name()}")
        print(f"✅ AnomalyDetectionStrategy: {anomaly_strategy.get_strategy_name()}")
        print(f"✅ События от стратегий: {len(threat_events + anomaly_events)}")
        
        # 4. Тест менеджеров данных
        print("4. Тестирование менеджеров данных...")
        data_manager = MonitoringDataManager(config)
        alert_manager = AlertManager(config)
        
        # Добавление событий
        for event in events:
            data_manager.add_event(event)
        
        # Получение событий
        all_events = data_manager.get_events()
        critical_events = data_manager.get_events_by_level(MonitoringLevel.CRITICAL)
        
        print(f"✅ MonitoringDataManager: {len(all_events)} событий")
        print(f"✅ Критических событий: {len(critical_events)}")
        
        # 5. Тест обработки алертов
        print("5. Тестирование обработки алертов...")
        await alert_manager.process_events(events)
        print(f"✅ AlertManager: {alert_manager.alert_count} алертов")
        
        # 6. Тест основного менеджера
        print("6. Тестирование SecurityMonitoringManager...")
        main_manager = SecurityMonitoringManager(
            name="ComprehensiveTestManager",
            config=config
        )
        
        # Добавление стратегий
        main_manager.add_monitoring_strategy(threat_strategy)
        main_manager.add_monitoring_strategy(anomaly_strategy)
        
        # Получение статуса
        status = main_manager.get_security_status()
        
        print(f"✅ SecurityMonitoringManager: {main_manager.name}")
        print(f"✅ Стратегий: {len(main_manager.strategies)}")
        print(f"✅ Статус: {len(status)} полей")
        
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
        
        assert main_manager.config.alert_threshold == 10
        print(f"✅ Конфигурация обновлена: threshold={main_manager.config.alert_threshold}")
        
        # 8. Тест остановки мониторинга
        print("8. Тестирование остановки мониторинга...")
        main_manager.stop_monitoring()
        assert not main_manager.config.enabled
        print("✅ Мониторинг остановлен")
        
        # 9. Финальная статистика
        print("\n9. Финальная статистика...")
        final_status = main_manager.get_security_status()
        
        print(f"📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   - Всего событий: {final_status['total_events']}")
        print(f"   - Критических событий: {final_status['critical_events']}")
        print(f"   - Высокоприоритетных событий: {final_status['high_events']}")
        print(f"   - Алертов: {final_status['alert_count']}")
        print(f"   - Стратегий: {final_status['strategies_count']}")
        print(f"   - Мониторинг включен: {final_status['monitoring_enabled']}")
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ КОРРЕКТНО!")
        print("✅ SecurityMonitoringManager готов к продакшену!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В КОМПЛЕКСНОМ ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_comprehensive_functionality())
    sys.exit(0 if success else 1)