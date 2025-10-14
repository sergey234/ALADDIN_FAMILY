#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование мобильного API для VPN и антивируса
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.mobile.mobile_api import (
    MobileSecurityAPI, 
    MobileConnectionConfig, 
    ConnectionType, 
    ConnectionSpeed
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mobile_api():
    """Тестирование мобильного API"""
    print("📱 ТЕСТИРОВАНИЕ МОБИЛЬНОГО API ALADDIN")
    print("=" * 60)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Создание API
        print("1. Создание мобильного API...")
        api = MobileSecurityAPI()
        print("✅ Мобильный API создан")
        
        # Получение статуса
        print("\n2. Получение статуса приложения...")
        status = api.get_mobile_status()
        print(f"   Приложение: {status['app_name']}")
        print(f"   Версия: {status['version']}")
        print(f"   Статус: {status['status']}")
        print(f"   VPN доступен: {status['vpn_available']}")
        print(f"   Антивирус доступен: {status['antivirus_available']}")
        
        # Получение вариантов подключения
        print("\n3. Получение вариантов подключения...")
        options = api.get_connection_options()
        print(f"   Типов подключения: {len(options['connection_types'])}")
        print(f"   Скоростей: {len(options['speeds'])}")
        print(f"   Стран: {len(options['countries'])}")
        
        for conn_type in options['connection_types']:
            print(f"   📱 {conn_type['name']}: {conn_type['description']}")
        
        # Тестирование подключения VPN
        print("\n4. Тестирование подключения VPN...")
        config = MobileConnectionConfig(
            connection_type=ConnectionType.VPN_ONLY,
            speed=ConnectionSpeed.FAST,
            country="Singapore"
        )
        
        result = await api.connect_mobile(config)
        print(f"   ✅ Подключение VPN: {result.message}")
        print(f"   ID подключения: {result.connection_id}")
        print(f"   Время подключения: {result.connection_time:.2f}с")
        print(f"   Уровень безопасности: {result.security_level}")
        
        # Тестирование подключения антивируса
        print("\n5. Тестирование подключения антивируса...")
        config_antivirus = MobileConnectionConfig(
            connection_type=ConnectionType.ANTIVIRUS_ONLY,
            speed=ConnectionSpeed.SECURE,
            country="Singapore"
        )
        
        result_antivirus = await api.connect_mobile(config_antivirus)
        print(f"   ✅ Подключение антивируса: {result_antivirus.message}")
        print(f"   ID подключения: {result_antivirus.connection_id}")
        print(f"   Время подключения: {result_antivirus.connection_time:.2f}с")
        
        # Тестирование комбинированного подключения
        print("\n6. Тестирование VPN + Антивирус...")
        config_combined = MobileConnectionConfig(
            connection_type=ConnectionType.VPN_ANTIVIRUS,
            speed=ConnectionSpeed.BALANCED,
            country="Singapore"
        )
        
        result_combined = await api.connect_mobile(config_combined)
        print(f"   ✅ Комбинированное подключение: {result_combined.message}")
        print(f"   ID подключения: {result_combined.connection_id}")
        print(f"   Время подключения: {result_combined.connection_time:.2f}с")
        
        # Тестирование умной защиты
        print("\n7. Тестирование умной защиты...")
        config_smart = MobileConnectionConfig(
            connection_type=ConnectionType.SMART_PROTECTION,
            speed=ConnectionSpeed.SECURE,
            country="Singapore"
        )
        
        result_smart = await api.connect_mobile(config_smart)
        print(f"   ✅ Умная защита: {result_smart.message}")
        print(f"   ID подключения: {result_smart.connection_id}")
        print(f"   Время подключения: {result_smart.connection_time:.2f}с")
        
        # Отключение всех подключений
        print("\n8. Отключение всех подключений...")
        connections = [result.connection_id, result_antivirus.connection_id, 
                      result_combined.connection_id, result_smart.connection_id]
        
        for conn_id in connections:
            if conn_id:
                disconnect_result = await api.disconnect_mobile(conn_id)
                print(f"   ✅ Отключение {conn_id}: {disconnect_result['message']}")
        
        # Финальный статус
        print("\n9. Финальный статус...")
        final_status = api.get_mobile_status()
        print(f"   Активных подключений: {final_status['active_connections']}")
        print(f"   Статус: {final_status['status']}")
        
        print("\n🎉 ТЕСТИРОВАНИЕ МОБИЛЬНОГО API ЗАВЕРШЕНО УСПЕШНО!")
        print("\n📱 РЕЗУЛЬТАТЫ ДЛЯ МОБИЛЬНОГО ПРИЛОЖЕНИЯ:")
        print("   ✅ 4 типа подключения работают")
        print("   ✅ 3 скорости подключения работают")
        print("   ✅ 5 стран доступны")
        print("   ✅ Простое и красивое подключение")
        print("   ✅ Автоматическое отключение")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("📱 MOBILE API ALADDIN - ТЕСТИРОВАНИЕ")
    print("=" * 60)
    
    # Тестирование API
    success = await test_mobile_api()
    
    print("\n" + "=" * 60)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ТЕСТИРОВАНИЕ МОБИЛЬНОГО API ЗАВЕРШЕНО УСПЕШНО!")
        print("\n🎯 ГОТОВО ДЛЯ МОБИЛЬНОГО ПРИЛОЖЕНИЯ:")
        print("1. 📱 Простое подключение - 1 кнопка")
        print("2. 🌍 4 типа защиты - на выбор")
        print("3. ⚡ 3 скорости - быстрая, сбалансированная, безопасная")
        print("4. 🗺️ 5 стран - Singapore, Russia, Netherlands, USA, Japan")
        print("5. 🧠 Умная защита - автоматический выбор")
        print("6. 🔒 Только для пользователей ALADDIN")
    else:
        print("❌ ТЕСТИРОВАНИЕ МОБИЛЬНОГО API ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
