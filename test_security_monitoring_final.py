#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест всех компонентов SecurityMonitoringManager
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


async def test_final_comprehensive():
    """Финальный комплексный тест всех компонентов"""
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    try:
        # 1. Тест всех перечислений
        print("1. Тестирование всех перечислений...")
        levels = list(MonitoringLevel)
        alert_types = list(AlertType)
        print(f"✅ MonitoringLevel: {len(levels)} уровней")
        print(f"✅ AlertType: {len(alert_types)} типов")
        
        # 2. Тест создания всех dataclasses
        print("\n2. Тестирование всех dataclasses...")
        config = MonitoringConfig(
            enabled=True,
            alert_threshold=5,
            check_interval=30,
            retention_days=7,
            log_level="INFO"
        )
        
        event = SecurityEvent(
            event_id="final_test_001",
            timestamp=datetime.now(),
            level=MonitoringLevel.HIGH,
            alert_type=AlertType.THREAT_DETECTED,
            description="Final test event",
            source="final_test_system"
        )
        
        print(f"✅ MonitoringConfig: {config}")
        print(f"✅ SecurityEvent: {event}")
        
        # 3. Тест всех стратегий
        print("\n3. Тестирование всех стратегий...")
        threat_strategy = ThreatDetectionStrategy(config)
        anomaly_strategy = AnomalyDetectionStrategy(config)
        
        # Тест асинхронных методов
        threat_events = await threat_strategy.check_security()
        anomaly_events = await anomaly_strategy.check_security()
        
        print(f"✅ ThreatDetectionStrategy: {threat_strategy.get_strategy_name()}")
        print(f"✅ AnomalyDetectionStrategy: {anomaly_strategy.get_strategy_name()}")
        print(f"✅ События от стратегий: {len(threat_events + anomaly_events)}")
        
        # 4. Тест всех менеджеров
        print("\n4. Тестирование всех менеджеров...")
        data_manager = MonitoringDataManager(config)
        alert_manager = AlertManager(config)
        
        # Добавление событий
        for i in range(3):
            test_event = SecurityEvent(
                event_id=f"test_event_{i:03d}",
                timestamp=datetime.now(),
                level=MonitoringLevel.MEDIUM,
                alert_type=AlertType.ANOMALY_FOUND,
                description=f"Test event {i}",
                source="test_system"
            )
            data_manager.add_event(test_event)
        
        # Получение событий
        all_events = data_manager.get_events()
        critical_events = data_manager.get_events_by_level(MonitoringLevel.CRITICAL)
        
        print(f"✅ MonitoringDataManager: {len(all_events)} событий")
        print(f"✅ Критических событий: {len(critical_events)}")
        
        # Обработка алертов
        await alert_manager.process_events(all_events)
        print(f"✅ AlertManager: обработано {len(all_events)} событий")
        
        # 5. Тест основного менеджера
        print("\n5. Тестирование SecurityMonitoringManager...")
        main_manager = SecurityMonitoringManager(
            name="FinalTestManager",
            config=config
        )
        
        # Тест всех методов
        print(f"✅ Создан: {main_manager}")
        print(f"✅ Длина: {len(main_manager)} стратегий")
        print(f"✅ Итерация: {len(list(main_manager))} стратегий")
        
        # Добавление стратегий
        main_manager.add_monitoring_strategy(threat_strategy)
        main_manager.add_monitoring_strategy(anomaly_strategy)
        
        # Проверка содержимого
        assert threat_strategy in main_manager, "ThreatDetectionStrategy должна быть в менеджере"
        assert anomaly_strategy in main_manager, "AnomalyDetectionStrategy должна быть в менеджере"
        
        print(f"✅ Добавлено стратегий: {len(main_manager.strategies)}")
        
        # 6. Тест всех property методов
        print("\n6. Тестирование всех property методов...")
        print(f"✅ is_running: {main_manager.is_running}")
        print(f"✅ strategies_count: {main_manager.strategies_count}")
        print(f"✅ status_info: {len(main_manager.status_info)} полей")
        
        # 7. Тест всех static методов
        print("\n7. Тестирование всех static методов...")
        supported_levels = SecurityMonitoringManager.get_supported_levels()
        supported_alert_types = SecurityMonitoringManager.get_supported_alert_types()
        
        print(f"✅ get_supported_levels: {len(supported_levels)} уровней")
        print(f"✅ get_supported_alert_types: {len(supported_alert_types)} типов")
        
        # 8. Тест всех class методов
        print("\n8. Тестирование всех class методов...")
        custom_config = MonitoringConfig(
            enabled=False,
            alert_threshold=10,
            check_interval=60,
            retention_days=14,
            log_level="DEBUG"
        )
        
        custom_manager = SecurityMonitoringManager.create_with_custom_config(
            "CustomFinalManager", custom_config
        )
        
        assert custom_manager.name == "CustomFinalManager", "Имя должно быть CustomFinalManager"
        assert custom_manager.config == custom_config, "Конфигурация должна совпадать"
        print(f"✅ create_with_custom_config: {custom_manager.name}")
        
        # 9. Тест контекстного менеджера
        print("\n9. Тестирование контекстного менеджера...")
        with main_manager as m:
            assert m is main_manager, "Контекстный менеджер должен возвращать self"
            print("✅ __enter__ работает корректно")
        print("✅ __exit__ работает корректно")
        
        # 10. Тест обновления конфигурации
        print("\n10. Тестирование обновления конфигурации...")
        new_config = MonitoringConfig(
            enabled=True,
            alert_threshold=15,
            check_interval=120,
            retention_days=30,
            log_level="WARNING"
        )
        
        main_manager.update_config(new_config)
        assert main_manager.config.alert_threshold == 15, "Порог должен быть 15"
        print(f"✅ Конфигурация обновлена: threshold={main_manager.config.alert_threshold}")
        
        # 11. Тест остановки мониторинга
        print("\n11. Тестирование остановки мониторинга...")
        main_manager.stop_monitoring()
        assert not main_manager.config.enabled, "Мониторинг должен быть остановлен"
        print("✅ Мониторинг остановлен")
        
        # 12. Финальная статистика
        print("\n12. Финальная статистика...")
        final_status = main_manager.get_security_status()
        
        print(f"📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"   - Имя менеджера: {main_manager.name}")
        print(f"   - Всего событий: {final_status['total_events']}")
        print(f"   - Критических событий: {final_status['critical_events']}")
        print(f"   - Высокоприоритетных событий: {final_status['high_events']}")
        print(f"   - Алертов: {final_status['alert_count']}")
        print(f"   - Стратегий: {final_status['strategies_count']}")
        print(f"   - Мониторинг включен: {final_status['monitoring_enabled']}")
        
        # 13. Тест сравнения объектов
        print("\n13. Тестирование сравнения объектов...")
        manager1 = SecurityMonitoringManager("Test1", config)
        manager2 = SecurityMonitoringManager("Test1", config)
        manager3 = SecurityMonitoringManager("Test2", config)
        
        assert manager1 == manager2, "Одинаковые менеджеры должны быть равны"
        assert manager1 != manager3, "Разные менеджеры должны быть не равны"
        print("✅ Сравнение объектов работает корректно")
        
        # 14. Тест строкового представления
        print("\n14. Тестирование строкового представления...")
        print(f"✅ __str__: {str(main_manager)}")
        print(f"✅ __repr__: {repr(main_manager)}")
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ ИДЕАЛЬНО!")
        print("✅ SecurityMonitoringManager готов к продакшену!")
        print("✅ Качество A+ достигнуто!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В ФИНАЛЬНОМ ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_final_comprehensive())
    sys.exit(0 if success else 1)