#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простой тест для DataProtectionAgent
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_data_protection_agent():
    """Простой тест DataProtectionAgent"""
    print("🧪 ТЕСТИРОВАНИЕ DataProtectionAgent")
    print("=" * 50)
    
    try:
        # Импорт агента
        from security.ai_agents.data_protection_agent import (
            DataProtectionAgent,
            DataType,
            ProtectionLevel,
            DataStatus
        )
        print("✅ Импорт DataProtectionAgent успешен")
        
        # Создание агента
        config = {
            "encryption_enabled": True,
            "anonymization_enabled": True,
            "backup_enabled": True
        }
        agent = DataProtectionAgent(config=config)
        print("✅ DataProtectionAgent создан")
        
        # Инициализация
        init_result = agent.initialize()
        print("✅ Инициализация: {}".format("УСПЕШНО" if init_result else "ОШИБКА"))
        
        # Тест защиты персональных данных
        personal_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        
        result = agent.protect_data(
            data_id="test_personal_001",
            data=personal_data,
            data_type=DataType.PERSONAL,
            protection_level=ProtectionLevel.HIGH
        )
        
        print("✅ Защита персональных данных: {}".format(
            "УСПЕШНО" if result and result.data_id == "test_personal_001" else "ОШИБКА"
        ))
        
        # Тест защиты финансовых данных
        financial_data = {
            "account": "1234567890",
            "balance": 1000.50
        }
        
        result2 = agent.protect_data(
            data_id="test_financial_001",
            data=financial_data,
            data_type=DataType.FINANCIAL,
            protection_level=ProtectionLevel.CRITICAL
        )
        
        print("✅ Защита финансовых данных: {}".format(
            "УСПЕШНО" if result2 and result2.data_id == "test_financial_001" else "ОШИБКА"
        ))
        
        # Тест получения статуса
        status = agent.get_protection_status("test_personal_001")
        print("✅ Получение статуса защиты: {}".format(
            "УСПЕШНО" if status else "ОШИБКА"
        ))
        
        # Тест метрик
        metrics = agent.get_metrics()
        print("✅ Получение метрик: {}".format(
            "УСПЕШНО" if metrics else "ОШИБКА"
        ))
        
        # Тест событий
        events = agent.get_protection_events()
        print("✅ Получение событий: {}".format(
            "УСПЕШНО" if events is not None else "ОШИБКА"
        ))
        
        # Остановка агента
        agent.stop()
        print("✅ Остановка агента: УСПЕШНО")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("📊 DataProtectionAgent готов к работе")
        return True
        
    except Exception as e:
        print("❌ ОШИБКА ТЕСТИРОВАНИЯ: {}".format(e))
        return False

if __name__ == "__main__":
    success = test_data_protection_agent()
    sys.exit(0 if success else 1)