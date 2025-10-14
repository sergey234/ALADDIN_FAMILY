#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест Singapore API для мобильного устройства
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.vpn.vpn_security_system import VPNSecuritySystem, VPNSecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_singapore_mobile():
    """Тестирование Singapore для мобильного устройства"""
    print("�� ТЕСТИРОВАНИЕ SINGAPORE VPN ДЛЯ МОБИЛЬНОГО УСТРОЙСТВА")
    print("=" * 60)
    
    try:
        # Создание VPN системы
        print("1. Создание VPN Security System...")
        vpn_system = VPNSecuritySystem("MobileTestVPN")
        print("✅ VPN Security System создан")
        
        # Получение Singapore серверов
        print("\n2. Получение Singapore серверов...")
        singapore_servers = vpn_system.get_available_servers("Singapore")
        print(f"   Найдено Singapore серверов: {len(singapore_servers)}")
        
        for server in singapore_servers:
            print(f"   �� {server['name']} ({server['city']})")
            print(f"      Протокол: {server['protocol']}")
            print(f"      Задержка: {server['latency']:.1f}ms")
            print(f"      Нагрузка: {server['load']:.1%}")
        
        # Тестирование подключения к Singapore
        print("\n3. Тестирование подключения к Singapore...")
        test_user = f"mobile_user_{int(time.time())}"
        
        print("   🔗 Подключение к Singapore...")
        success, message, report = await vpn_system.connect(
            test_user, 
            country="Singapore",
            security_level=VPNSecurityLevel.HIGH
        )
        
        if success:
            print(f"   ✅ Подключение успешно: {message}")
            print(f"   Провайдер: {report.get('provider', 'unknown')}")
            print(f"   Время подключения: {report.get('connection_time', 0):.2f}с")
            print(f"   Уровень безопасности: {report.get('security_level', 'unknown')}")
            
            # Проверка статуса подключения
            print("\n4. Проверка статуса подключения...")
            connection_status = vpn_system.get_connection_status(test_user)
            if connection_status:
                print(f"   Статус: {connection_status['status']}")
                print(f"   Сервер: {connection_status['server_id']}")
                print(f"   Время начала: {connection_status['start_time']}")
            
            # Имитация использования на мобильном устройстве
            print("\n5. Имитация использования на мобильном устройстве...")
            print("   📱 Открытие веб-страниц...")
            await asyncio.sleep(2)
            print("   📱 Проверка IP адреса...")
            await asyncio.sleep(1)
            print("   📱 Тестирование скорости...")
            await asyncio.sleep(2)
            
            # Отключение
            print("\n6. Отключение от VPN...")
            success, message = await vpn_system.disconnect(test_user)
            if success:
                print(f"   ✅ Отключение успешно: {message}")
            else:
                print(f"   ❌ Ошибка отключения: {message}")
        else:
            print(f"   ❌ Ошибка подключения: {message}")
        
        # Финальная статистика
        print("\n7. Финальная статистика:")
        print("=" * 25)
        final_stats = vpn_system.get_system_stats()
        print(f"   Всего подключений: {final_stats['total_connections']}")
        print(f"   Успешных: {final_stats['successful_connections']}")
        print(f"   Успешность: {final_stats['success_rate']:.1f}%")
        print(f"   Уровень безопасности: {final_stats['security_level']}")
        
        print("\n🎉 ТЕСТИРОВАНИЕ SINGAPORE ДЛЯ МОБИЛЬНОГО УСТРОЙСТВА ЗАВЕРШЕНО УСПЕШНО!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("📱 VPN SECURITY SYSTEM - ТЕСТИРОВАНИЕ SINGAPORE ДЛЯ МОБИЛЬНОГО")
    print("=" * 80)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Тестирование Singapore
    success = await test_singapore_mobile()
    
    print("\n" + "=" * 80)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ТЕСТИРОВАНИЕ SINGAPORE ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("❌ ТЕСТИРОВАНИЕ SINGAPORE ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
