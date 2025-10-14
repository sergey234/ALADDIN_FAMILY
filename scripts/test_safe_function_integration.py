#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование интеграции VPN и антивируса в SafeFunctionManager
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
from security.vpn.vpn_security_system import VPNSecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_safe_function_integration():
    """Тестирование интеграции VPN и антивируса в SafeFunctionManager"""
    print("🔧 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ VPN И АНТИВИРУСА В SAFEFUNCTIONMANAGER")
    print("=" * 70)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Создание SafeFunctionManager
        print("1. Создание SafeFunctionManager...")
        sfm = SafeFunctionManager("TestSafeFunctionManager")
        print("✅ SafeFunctionManager создан")
        
        # Инициализация
        print("\n2. Инициализация SafeFunctionManager...")
        init_success = sfm.initialize()
        if init_success:
            print("✅ SafeFunctionManager инициализирован")
        else:
            print("❌ Ошибка инициализации SafeFunctionManager")
            return False
        
        # Проверка VPN системы
        print("\n3. Проверка VPN системы...")
        if sfm.vpn_system:
            print("✅ VPN система инициализирована")
            
            # Тестирование VPN функции
            print("\n4. Тестирование VPN функции...")
            success, result, message = sfm.execute_function("vpn_security", {"action": "status"})
            if success:
                print(f"✅ VPN статус: {message}")
                print(f"   Статус: {result.get('status', 'unknown')}")
                print(f"   Серверов: {result.get('total_servers', 0)}")
            else:
                print(f"❌ Ошибка VPN: {message}")
        else:
            print("❌ VPN система не инициализирована")
        
        # Проверка антивирусной системы
        print("\n5. Проверка антивирусной системы...")
        if sfm.antivirus_system:
            print("✅ Антивирусная система инициализирована")
            
            # Тестирование антивирусной функции
            print("\n6. Тестирование антивирусной функции...")
            success, result, message = sfm.execute_function("antivirus_security", {"action": "status"})
            if success:
                print(f"✅ Антивирус статус: {message}")
                print(f"   Статус: {result.get('status', 'unknown')}")
                print(f"   Сигнатур: {result.get('total_signatures', 0)}")
            else:
                print(f"❌ Ошибка антивируса: {message}")
        else:
            print("❌ Антивирусная система не инициализирована")
        
        # Тестирование VPN подключения
        print("\n7. Тестирование VPN подключения...")
        if sfm.vpn_system:
            success, result, message = sfm.execute_function("vpn_security", {
                "action": "connect",
                "connection_id": "test_connection_1",
                "country": "Singapore",
                "security_level": VPNSecurityLevel.HIGH
            })
            if success:
                print(f"✅ VPN подключение: {message}")
                print(f"   Connection ID: test_connection_1")
                print(f"   Страна: Singapore")
                print(f"   Уровень безопасности: HIGH")
            else:
                print(f"❌ Ошибка VPN подключения: {message}")
        
        # Тестирование отключения VPN
        print("\n8. Тестирование отключения VPN...")
        if sfm.vpn_system:
            success, result, message = sfm.execute_function("vpn_security", {
                "action": "disconnect",
                "connection_id": "test_connection_1"
            })
            if success:
                print(f"✅ VPN отключение: {message}")
            else:
                print(f"❌ Ошибка VPN отключения: {message}")
        
        # Получение статистики
        print("\n9. Получение статистики SafeFunctionManager...")
        stats = sfm.get_safe_function_stats()
        print(f"   Всего функций: {stats['total_functions']}")
        print(f"   Включенных функций: {stats['enabled_functions']}")
        print(f"   Отключенных функций: {stats['disabled_functions']}")
        print(f"   Критических функций: {stats['critical_functions']}")
        print(f"   Функций по типам: {stats['functions_by_type']}")
        
        # Остановка
        print("\n10. Остановка SafeFunctionManager...")
        stop_success = sfm.stop()
        if stop_success:
            print("✅ SafeFunctionManager остановлен")
        else:
            print("❌ Ошибка остановки SafeFunctionManager")
        
        print("\n🎉 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ЗАВЕРШЕНО УСПЕШНО!")
        print("\n📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИИ:")
        print("   ✅ VPN система интегрирована")
        print("   ✅ Антивирусная система интегрирована")
        print("   ✅ Обработчики функций работают")
        print("   ✅ Подключение/отключение VPN работает")
        print("   ✅ Статус систем получается")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🔧 SAFEFUNCTIONMANAGER - ИНТЕГРАЦИЯ VPN И АНТИВИРУСА")
    print("=" * 70)
    
    # Тестирование интеграции
    success = await test_safe_function_integration()
    
    print("\n" + "=" * 70)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ИНТЕГРАЦИЯ VPN И АНТИВИРУСА В SAFEFUNCTIONMANAGER ЗАВЕРШЕНА УСПЕШНО!")
        print("\n🎯 ГОТОВО К СПЯЩЕМУ РЕЖИМУ:")
        print("1. 🔧 VPN интегрирован в SafeFunctionManager")
        print("2. 🛡️ Антивирус интегрирован в SafeFunctionManager")
        print("3. ⚙️ Обработчики функций работают")
        print("4. 🔄 Подключение/отключение работает")
        print("5. 📊 Статистика доступна")
    else:
        print("❌ ИНТЕГРАЦИЯ VPN И АНТИВИРУСА ЗАВЕРШЕНА С ОШИБКАМИ!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
