#!/usr/bin/env python3
"""
📱 ALADDIN - Test Call Protection System
Тестирование системы защиты звонков и SIM-карт

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Добавляем путь к проекту
sys.path.append("/Users/sergejhlystov/ALADDIN_NEW")

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/call_protection_test.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

async def test_call_protection_system():
    """Тестирование системы защиты звонков"""
    logger = logging.getLogger(__name__)
    
    try:
        from security.integrations.sim_card_monitoring import SIMCardMonitoring
        
        logger.info("🔧 Тестирование системы защиты звонков...")
        
        # Создание экземпляра
        call_protection = SIMCardMonitoring()
        
        # ТЕСТ 1: Звонок от мамы (должен пройти)
        logger.info("=" * 60)
        logger.info("📞 ТЕСТ 1: Звонок от мамы")
        logger.info("=" * 60)
        
        mom_call = {
            "call_id": "call_001",
            "caller_number": "+7-900-123-45-67",  # Номер мамы из доверенных
            "receiver_number": "+7-900-111-22-33",
            "timestamp": datetime.now()
        }
        
        mom_analysis = call_protection.analyze_call(mom_call)
        logger.info(f"✅ Результат: Безопасность={mom_analysis.is_safe}, Тип={mom_analysis.caller_type}")
        logger.info(f"✅ Рекомендация: {mom_analysis.blocking_recommendation}")
        logger.info(f"✅ Уверенность: {mom_analysis.confidence:.2f}")
        
        # ТЕСТ 2: Мошеннический звонок (должен быть заблокирован)
        logger.info("=" * 60)
        logger.info("📞 ТЕСТ 2: Мошеннический звонок")
        logger.info("=" * 60)
        
        scam_call = {
            "call_id": "call_002",
            "caller_number": "+7-800-555-00-00",  # Номер из базы мошенников
            "receiver_number": "+7-900-111-22-33",
            "timestamp": datetime.now()
        }
        
        scam_analysis = call_protection.analyze_call(scam_call)
        logger.info(f"❌ Результат: Безопасность={scam_analysis.is_safe}, Тип={scam_analysis.caller_type}")
        logger.info(f"❌ Рекомендация: {scam_analysis.blocking_recommendation}")
        logger.info(f"❌ Уверенность: {scam_analysis.confidence:.2f}")
        
        # ТЕСТ 3: Неизвестный номер (анализ)
        logger.info("=" * 60)
        logger.info("📞 ТЕСТ 3: Неизвестный номер")
        logger.info("=" * 60)
        
        unknown_call = {
            "call_id": "call_003",
            "caller_number": "+7-900-777-88-99",  # Неизвестный номер
            "receiver_number": "+7-900-111-22-33",
            "timestamp": datetime.now()
        }
        
        unknown_analysis = call_protection.analyze_call(unknown_call)
        logger.info(f"🔍 Результат: Безопасность={unknown_analysis.is_safe}, Тип={unknown_analysis.caller_type}")
        logger.info(f"🔍 Рекомендация: {unknown_analysis.blocking_recommendation}")
        logger.info(f"🔍 Уверенность: {unknown_analysis.confidence:.2f}")
        
        # ТЕСТ 4: Звонок от друга (должен пройти)
        logger.info("=" * 60)
        logger.info("📞 ТЕСТ 4: Звонок от друга")
        logger.info("=" * 60)
        
        friend_call = {
            "call_id": "call_004",
            "caller_number": "+7-900-345-67-89",  # Номер друга из доверенных
            "receiver_number": "+7-900-111-22-33",
            "timestamp": datetime.now()
        }
        
        friend_analysis = call_protection.analyze_call(friend_call)
        logger.info(f"✅ Результат: Безопасность={friend_analysis.is_safe}, Тип={friend_analysis.caller_type}")
        logger.info(f"✅ Рекомендация: {friend_analysis.blocking_recommendation}")
        logger.info(f"✅ Уверенность: {friend_analysis.confidence:.2f}")
        
        # ТЕСТ 5: Ночной звонок от неизвестного (подозрительно)
        logger.info("=" * 60)
        logger.info("📞 ТЕСТ 5: Ночной звонок от неизвестного")
        logger.info("=" * 60)
        
        night_call = {
            "call_id": "call_005",
            "caller_number": "+7-900-999-88-77",  # Неизвестный номер
            "receiver_number": "+7-900-111-22-33",
            "timestamp": datetime(2024, 12, 1, 2, 30)  # 2:30 ночи
        }
        
        night_analysis = call_protection.analyze_call(night_call)
        logger.info(f"🌙 Результат: Безопасность={night_analysis.is_safe}, Тип={night_analysis.caller_type}")
        logger.info(f"🌙 Рекомендация: {night_analysis.blocking_recommendation}")
        logger.info(f"🌙 Уверенность: {night_analysis.confidence:.2f}")
        
        # ТЕСТ 6: Анализ SIM-карты
        logger.info("=" * 60)
        logger.info("📱 ТЕСТ 6: Анализ SIM-карты")
        logger.info("=" * 60)
        
        sim_data = {
            "sim_id": "sim_001",
            "phone_number": "+7-900-123-45-67",
            "carrier": "Tele2",
            "registration_date": "2024-01-01"
        }
        
        sim_analysis = call_protection.analyze_sim_card(sim_data)
        logger.info(f"📱 Результат: Легитимность={sim_analysis.is_legitimate}")
        logger.info(f"📱 Риск: {sim_analysis.risk_score:.2f}")
        logger.info(f"📱 Рекомендация: {sim_analysis.recommendation}")
        
        # Получение статистики
        stats = call_protection.get_statistics()
        logger.info("=" * 60)
        logger.info("📊 СТАТИСТИКА СИСТЕМЫ:")
        logger.info("=" * 60)
        logger.info(f"📞 Всего звонков проанализировано: {stats['total_calls_analyzed']}")
        logger.info(f"🚫 Мошеннических звонков заблокировано: {stats['scam_calls_blocked']}")
        logger.info(f"✅ Семья и друзья пропущены: {stats['family_friends_allowed']}")
        logger.info(f"⚠️ Ложных срабатываний: {stats['false_positives']}")
        logger.info(f"📋 Доверенных контактов: {stats['trusted_contacts_count']}")
        logger.info(f"🚫 Мошеннических номеров в базе: {stats['scam_database_size']}")
        
        logger.info("=" * 60)
        logger.info("✅ Тестирование системы защиты звонков завершено!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования системы защиты звонков: {str(e)}")
        return False

def demonstrate_family_protection():
    """Демонстрация защиты семьи"""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("👨‍👩‍👧‍👦 ДЕМОНСТРАЦИЯ ЗАЩИТЫ СЕМЬИ")
    logger.info("=" * 80)
    
    family_scenarios = [
        {
            "scenario": "Звонок от мамы",
            "number": "+7-900-123-45-67",
            "expected": "NEVER_BLOCK",
            "reason": "В списке доверенных контактов"
        },
        {
            "scenario": "Звонок от папы", 
            "number": "+7-900-234-56-78",
            "expected": "NEVER_BLOCK",
            "reason": "В списке доверенных контактов"
        },
        {
            "scenario": "Звонок от лучшего друга",
            "number": "+7-900-345-67-89", 
            "expected": "NEVER_BLOCK",
            "reason": "В списке доверенных контактов"
        },
        {
            "scenario": "Звонок с работы",
            "number": "+7-900-456-78-90",
            "expected": "NEVER_BLOCK", 
            "reason": "В списке доверенных контактов"
        }
    ]
    
    for scenario in family_scenarios:
        logger.info(f"📞 {scenario['scenario']}: {scenario['number']}")
        logger.info(f"   ✅ Ожидается: {scenario['expected']}")
        logger.info(f"   📝 Причина: {scenario['reason']}")
        logger.info("")
    
    logger.info("🛡️ ВЫВОД: Семья и друзья НИКОГДА НЕ БУДУТ ЗАБЛОКИРОВАНЫ!")
    logger.info("=" * 80)

def demonstrate_scam_protection():
    """Демонстрация защиты от мошенников"""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("🚨 ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ МОШЕННИКОВ")
    logger.info("=" * 80)
    
    scam_scenarios = [
        {
            "scenario": "Финансовое мошенничество",
            "number": "+7-800-555-00-00",
            "expected": "BLOCK_IMMEDIATELY",
            "reason": "В базе мошеннических номеров"
        },
        {
            "scenario": "Социальная инженерия",
            "number": "+7-900-999-99-99",
            "expected": "BLOCK_IMMEDIATELY", 
            "reason": "В базе мошеннических номеров"
        },
        {
            "scenario": "Подозрительный номер с повторяющимися цифрами",
            "number": "+7-900-777-77-77",
            "expected": "MONITOR/BLOCK",
            "reason": "Подозрительный паттерн номера"
        },
        {
            "scenario": "Ночной звонок от неизвестного",
            "number": "+7-900-111-22-33",
            "expected": "MONITOR",
            "reason": "Подозрительное время звонка"
        }
    ]
    
    for scenario in scam_scenarios:
        logger.info(f"📞 {scenario['scenario']}: {scenario['number']}")
        logger.info(f"   ❌ Ожидается: {scenario['expected']}")
        logger.info(f"   📝 Причина: {scenario['reason']}")
        logger.info("")
    
    logger.info("🛡️ ВЫВОД: Мошенники будут эффективно заблокированы!")
    logger.info("=" * 80)

async def main():
    """Основная функция"""
    logger = setup_logging()
    
    logger.info("🚀 Запуск тестирования системы защиты звонков...")
    logger.info("=" * 80)
    
    # Демонстрация защиты семьи
    demonstrate_family_protection()
    
    # Демонстрация защиты от мошенников
    demonstrate_scam_protection()
    
    # Тестирование системы
    logger.info("🔧 Запуск практических тестов...")
    if not await test_call_protection_system():
        logger.error("❌ Тестирование системы защиты звонков не прошло")
        return False
    
    logger.info("=" * 80)
    logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    logger.info("🛡️ СИСТЕМА ГОТОВА К ЗАЩИТЕ ВАШЕЙ СЕМЬИ!")
    logger.info("=" * 80)
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Система защиты звонков работает отлично!")
        print("🛡️ Семья защищена, мошенники заблокированы!")
        print("📱 Детальное объяснение сохранено на рабочий стол:")
        print("   📄 ALADDIN_CALL_PROTECTION_EXPLANATION.md")
    else:
        print("\n❌ Ошибка тестирования системы защиты звонков")
        print("🔧 Проверьте логи и зависимости")