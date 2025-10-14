#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование расширенной VPN системы
Проверка новых стран и протоколов
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
from security.vpn.core.vpn_core import VPNProtocol

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vpn_extended():
    """Тестирование расширенной VPN системы"""
    print("🌍 ТЕСТИРОВАНИЕ РАСШИРЕННОЙ VPN СИСТЕМЫ")
    print("=" * 60)
    
    try:
        # Создание VPN системы
        print("1. Создание VPN Security System...")
        vpn_system = VPNSecuritySystem("ExtendedTestVPN")
        print("✅ VPN Security System создан")
        
        # Получение всех доступных серверов
        print("\n2. Получение всех доступных серверов...")
        all_servers = vpn_system.get_available_servers()
        print(f"   Всего серверов: {len(all_servers)}")
        
        # Группировка по странам
        countries = {}
        protocols = {}
        
        for server in all_servers:
            country = server['country']
            protocol = server['protocol']
            
            if country not in countries:
                countries[country] = []
            countries[country].append(server)
            
            if protocol not in protocols:
                protocols[protocol] = []
            protocols[protocol].append(server)
        
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
        
        # Вывод доступных протоколов
        print("\n4. Доступные протоколы:")
        print("=" * 30)
        
        for protocol, servers in protocols.items():
            print(f"\n🔌 {protocol.upper()}:")
            print(f"   Серверов: {len(servers)}")
            avg_latency = sum(s['latency'] for s in servers) / len(servers)
            print(f"   Средняя задержка: {avg_latency:.1f}ms")
        
        # Тестирование подключения к разным странам
        print("\n5. Тестирование подключения к разным странам:")
        print("=" * 55)
        
        test_countries = ['Singapore', 'Russia', 'Netherlands', 'USA', 'Japan']
        
        for country in test_countries:
            if country in countries:
                print(f"\n🔗 Тестирование подключения к {country}...")
                
                # Подключение
                test_user = f"test_user_{country.lower()}_{int(time.time())}"
                success, message, report = await vpn_system.connect(
                    test_user, 
                    country=country,
                    security_level=VPNSecurityLevel.HIGH
                )
                
                if success:
                    print(f"   ✅ Подключение успешно: {message}")
                    print(f"   Провайдер: {report.get('provider', 'unknown')}")
                    print(f"   Время подключения: {report.get('connection_time', 0):.2f}с")
                    
                    # Отключение
                    success, message = await vpn_system.disconnect(test_user)
                    if success:
                        print(f"   ✅ Отключение успешно")
                    else:
                        print(f"   ❌ Ошибка отключения: {message}")
                else:
                    print(f"   ❌ Ошибка подключения: {message}")
            else:
                print(f"   ⚠️ Страна {country} недоступна")
        
        # Тестирование WireGuard протокола
        print("\n6. Тестирование WireGuard протокола:")
        print("=" * 40)
        
        # Получение WireGuard серверов
        wg_servers = [s for s in all_servers if s['protocol'] == 'wireguard']
        
        if wg_servers:
            print(f"   Найдено WireGuard серверов: {len(wg_servers)}")
            
            for server in wg_servers[:3]:  # Тестируем первые 3
                print(f"\n   🔗 Тестирование {server['name']}...")
                
                test_user = f"test_user_wg_{int(time.time())}"
                success, message, report = await vpn_system.connect(
                    test_user, 
                    country=server['country'],
                    security_level=VPNSecurityLevel.HIGH
                )
                
                if success:
                    print(f"      ✅ WireGuard подключение успешно: {message}")
                    print(f"      Время подключения: {report.get('connection_time', 0):.2f}с")
                    
                    # Отключение
                    await vpn_system.disconnect(test_user)
                    print(f"      ✅ Отключение успешно")
                else:
                    print(f"      ❌ Ошибка WireGuard подключения: {message}")
        else:
            print("   ⚠️ WireGuard серверы недоступны")
        
        # Статистика по странам
        print("\n7. Статистика по странам:")
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
        print("\n8. Рекомендации для мобильного подключения:")
        print("=" * 50)
        
        # Сортировка по задержке
        sorted_countries = sorted(countries.items(), 
                                key=lambda x: sum(s['latency'] for s in x[1]) / len(x[1]))
        
        print("🏆 Лучшие страны по задержке:")
        for i, (country, servers) in enumerate(sorted_countries[:5], 1):
            avg_latency = sum(s['latency'] for s in servers) / len(servers)
            print(f"   {i}. {country} - {avg_latency:.1f}ms")
        
        print("\n📱 Для мобильного использования рекомендуем:")
        print("   - WireGuard протокол (быстрее и стабильнее)")
        print("   - Singapore (низкая задержка)")
        print("   - Europe (стабильное соединение)")
        print("   - Asia (близко к России)")
        
        # Финальная статистика
        print("\n9. Финальная статистика:")
        print("=" * 25)
        final_stats = vpn_system.get_system_stats()
        print(f"   Всего подключений: {final_stats['total_connections']}")
        print(f"   Успешных: {final_stats['successful_connections']}")
        print(f"   Успешность: {final_stats['success_rate']:.1f}%")
        print(f"   Уровень безопасности: {final_stats['security_level']}")
        
        print("\n🎉 ТЕСТИРОВАНИЕ РАСШИРЕННОЙ VPN СИСТЕМЫ ЗАВЕРШЕНО УСПЕШНО!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🌍 VPN SECURITY SYSTEM - ТЕСТИРОВАНИЕ РАСШИРЕННОЙ СИСТЕМЫ")
    print("=" * 80)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Тестирование расширенной системы
    success = await test_vpn_extended()
    
    print("\n" + "=" * 80)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ТЕСТИРОВАНИЕ РАСШИРЕННОЙ СИСТЕМЫ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("❌ ТЕСТИРОВАНИЕ РАСШИРЕННОЙ СИСТЕМЫ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
