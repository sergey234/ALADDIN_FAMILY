#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка доступных стран для VPN подключения
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.vpn.vpn_security_system import VPNSecuritySystem, VPNSecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_vpn_countries():
    """Проверка доступных стран для VPN"""
    print("🌍 ПРОВЕРКА ДОСТУПНЫХ СТРАН ДЛЯ VPN ПОДКЛЮЧЕНИЯ")
    print("=" * 60)
    
    try:
        # Создание VPN системы
        print("1. Создание VPN Security System...")
        vpn_system = VPNSecuritySystem("CountryCheckVPN")
        print("✅ VPN Security System создан")
        
        # Получение всех доступных серверов
        print("\n2. Получение всех доступных серверов...")
        all_servers = vpn_system.get_available_servers()
        print(f"   Всего серверов: {len(all_servers)}")
        
        # Группировка по странам
        countries = {}
        for server in all_servers:
            country = server['country']
            if country not in countries:
                countries[country] = []
            countries[country].append(server)
        
        # Вывод доступных стран
        print("\n3. Доступные страны для подключения:")
        print("=" * 40)
        
        for country, servers in countries.items():
            print(f"\n🇺🇳 {country}:")
            for server in servers:
                print(f"   📍 {server['name']} ({server['city']})")
                print(f"      Протокол: {server['protocol']}")
                print(f"      Задержка: {server['latency']:.1f}ms")
                print(f"      Нагрузка: {server['load']:.1%}")
                print(f"      Тип: {server['type']}")
        
        # Тестирование подключения к каждой стране
        print("\n4. Тестирование подключения к каждой стране:")
        print("=" * 50)
        
        for country in countries.keys():
            print(f"\n🔗 Тестирование подключения к {country}...")
            
            # Подключение
            test_user = f"test_user_{country.lower()}_{int(datetime.now().timestamp())}"
            success, message, report = await vpn_system.connect(
                test_user, 
                country=country,
                security_level=VPNSecurityLevel.HIGH
            )
            
            if success:
                print(f"   ✅ Подключение успешно: {message}")
                print(f"   Провайдер: {report.get('provider', 'unknown')}")
                print(f"   Время подключения: {report.get('connection_time', 0):.2f}с")
                
                # Проверка статуса подключения
                connection_status = vpn_system.get_connection_status(test_user)
                if connection_status:
                    print(f"   Статус: {connection_status['status']}")
                    print(f"   Сервер: {connection_status['server_id']}")
                
                # Отключение
                success, message = await vpn_system.disconnect(test_user)
                if success:
                    print(f"   ✅ Отключение успешно")
                else:
                    print(f"   ❌ Ошибка отключения: {message}")
            else:
                print(f"   ❌ Ошибка подключения: {message}")
        
        # Статистика по странам
        print("\n5. Статистика по странам:")
        print("=" * 30)
        
        for country, servers in countries.items():
            total_servers = len(servers)
            avg_latency = sum(s['latency'] for s in servers) / total_servers
            avg_load = sum(s['load'] for s in servers) / total_servers
            
            print(f"🇺🇳 {country}:")
            print(f"   Серверов: {total_servers}")
            print(f"   Средняя задержка: {avg_latency:.1f}ms")
            print(f"   Средняя нагрузка: {avg_load:.1%}")
        
        # Рекомендации
        print("\n6. Рекомендации для мобильного подключения:")
        print("=" * 50)
        
        # Сортировка по задержке
        sorted_countries = sorted(countries.items(), 
                                key=lambda x: sum(s['latency'] for s in x[1]) / len(x[1]))
        
        print("🏆 Лучшие страны по задержке:")
        for i, (country, servers) in enumerate(sorted_countries[:3], 1):
            avg_latency = sum(s['latency'] for s in servers) / len(servers)
            print(f"   {i}. {country} - {avg_latency:.1f}ms")
        
        print("\n📱 Для мобильного использования рекомендуем:")
        print("   - Singapore (низкая задержка)")
        print("   - Russia (близкое расположение)")
        print("   - Europe (стабильное соединение)")
        
        # Финальная статистика
        print("\n7. Финальная статистика:")
        print("=" * 25)
        final_stats = vpn_system.get_system_stats()
        print(f"   Всего подключений: {final_stats['total_connections']}")
        print(f"   Успешных: {final_stats['successful_connections']}")
        print(f"   Успешность: {final_stats['success_rate']:.1f}%")
        print(f"   Уровень безопасности: {final_stats['security_level']}")
        
        print("\n🎉 ПРОВЕРКА СТРАН ЗАВЕРШЕНА УСПЕШНО!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в проверке стран: {e}")
        print(f"\n❌ ОШИБКА В ПРОВЕРКЕ СТРАН: {e}")
        return False

async def main():
    """Основная функция"""
    print("🌍 VPN SECURITY SYSTEM - ПРОВЕРКА ДОСТУПНЫХ СТРАН")
    print("=" * 70)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Проверка стран
    success = await check_vpn_countries()
    
    print("\n" + "=" * 70)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ПРОВЕРКА СТРАН ЗАВЕРШЕНА УСПЕШНО!")
    else:
        print("❌ ПРОВЕРКА СТРАН ЗАВЕРШЕНА С ОШИБКАМИ!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
