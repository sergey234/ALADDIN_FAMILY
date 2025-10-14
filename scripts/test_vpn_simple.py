#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое тестирование VPN Security System
Быстрый тест основных функций VPN
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

async def test_vpn_simple():
    """Простое тестирование VPN"""
    print("🚀 ПРОСТОЕ ТЕСТИРОВАНИЕ VPN SECURITY SYSTEM")
    print("=" * 50)
    
    try:
        # Создание VPN системы
        print("1. Создание VPN Security System...")
        vpn_system = VPNSecuritySystem("SimpleTestVPN")
        print("✅ VPN Security System создан")
        
        # Проверка статуса
        print("\n2. Проверка статуса системы...")
        status = vpn_system.get_status()
        print(f"   Статус: {status['status']}")
        print(f"   Сообщение: {status['message']}")
        
        # Получение статистики
        print("\n3. Получение статистики...")
        stats = vpn_system.get_system_stats()
        print(f"   Время работы: {stats['uptime']} секунд")
        print(f"   Уровень безопасности: {stats['security_level']}")
        
        # Получение доступных серверов
        print("\n4. Получение доступных серверов...")
        servers = vpn_system.get_available_servers()
        print(f"   Всего серверов: {len(servers)}")
        
        for server in servers[:3]:  # Показываем первые 3
            print(f"   - {server['name']} ({server['country']}) - {server['latency']:.1f}ms")
        
        # Тестирование подключения
        print("\n5. Тестирование подключения...")
        test_user = f"test_user_{int(time.time())}"
        
        # Подключение к Singapore
        print("   Подключение к Singapore...")
        success, message, report = await vpn_system.connect(
            test_user, 
            country="Singapore",
            security_level=VPNSecurityLevel.HIGH
        )
        
        if success:
            print(f"   ✅ Подключение успешно: {message}")
            print(f"   Провайдер: {report.get('provider', 'unknown')}")
            print(f"   Время подключения: {report.get('connection_time', 0):.2f}с")
            
            # Проверка статуса подключения
            print("\n6. Проверка статуса подключения...")
            connection_status = vpn_system.get_connection_status(test_user)
            if connection_status:
                print(f"   Статус: {connection_status['status']}")
                print(f"   Сервер: {connection_status['server_id']}")
            
            # Ожидание
            print("\n7. Ожидание 3 секунды...")
            await asyncio.sleep(3)
            
            # Отключение
            print("\n8. Отключение...")
            success, message = await vpn_system.disconnect(test_user)
            if success:
                print(f"   ✅ Отключение успешно: {message}")
            else:
                print(f"   ❌ Ошибка отключения: {message}")
        else:
            print(f"   ❌ Ошибка подключения: {message}")
        
        # Финальная статистика
        print("\n9. Финальная статистика...")
        final_stats = vpn_system.get_system_stats()
        print(f"   Всего подключений: {final_stats['total_connections']}")
        print(f"   Успешных: {final_stats['successful_connections']}")
        print(f"   Неудачных: {final_stats['failed_connections']}")
        print(f"   Успешность: {final_stats['success_rate']:.1f}%")
        
        print("\n🎉 ПРОСТОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🛡️ VPN SECURITY SYSTEM - ПРОСТОЕ ТЕСТИРОВАНИЕ")
    print("=" * 60)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Простое тестирование
    success = await test_vpn_simple()
    
    print("\n" + "=" * 60)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
