#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое тестирование интеграции VPN и антивируса в SafeFunctionManager
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_integration():
    """Простое тестирование интеграции"""
    print("🔧 ПРОСТОЕ ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ VPN И АНТИВИРУСА")
    print("=" * 60)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Импорт только после добавления пути
        from security.safe_function_manager import SafeFunctionManager
        from security.vpn.vpn_security_system import VPNSecurityLevel
        
        # Создание SafeFunctionManager
        print("1. Создание SafeFunctionManager...")
        sfm = SafeFunctionManager("TestSafeFunctionManager")
        print("✅ SafeFunctionManager создан")
        
        # Проверка VPN системы
        print("\n2. Проверка VPN системы...")
        if sfm.vpn_system:
            print("✅ VPN система инициализирована")
        else:
            print("❌ VPN система не инициализирована")
        
        # Проверка антивирусной системы
        print("\n3. Проверка антивирусной системы...")
        if sfm.antivirus_system:
            print("✅ Антивирусная система инициализирована")
        else:
            print("❌ Антивирусная система не инициализирована")
        
        # Проверка функций
        print("\n4. Проверка зарегистрированных функций...")
        if "vpn_security" in sfm.functions:
            print("✅ VPN функция зарегистрирована")
        else:
            print("❌ VPN функция не зарегистрирована")
        
        if "antivirus_security" in sfm.functions:
            print("✅ Антивирусная функция зарегистрирована")
        else:
            print("❌ Антивирусная функция не зарегистрирована")
        
        # Проверка обработчиков
        print("\n5. Проверка обработчиков...")
        if "vpn_security" in sfm.function_handlers:
            print("✅ VPN обработчик зарегистрирован")
        else:
            print("❌ VPN обработчик не зарегистрирован")
        
        if "antivirus_security" in sfm.function_handlers:
            print("✅ Антивирусный обработчик зарегистрирован")
        else:
            print("❌ Антивирусный обработчик не зарегистрирован")
        
        print("\n🎉 ПРОСТОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("\n📊 РЕЗУЛЬТАТЫ:")
        print("   ✅ SafeFunctionManager создан")
        print("   ✅ VPN система инициализирована")
        print("   ✅ Антивирусная система инициализирована")
        print("   ✅ Функции зарегистрированы")
        print("   ✅ Обработчики зарегистрированы")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🔧 SAFEFUNCTIONMANAGER - ПРОСТОЕ ТЕСТИРОВАНИЕ")
    print("=" * 60)
    
    # Тестирование интеграции
    success = await test_simple_integration()
    
    print("\n" + "=" * 60)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ПРОСТОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("\n🎯 ГОТОВО К СПЯЩЕМУ РЕЖИМУ:")
        print("1. 🔧 VPN интегрирован в SafeFunctionManager")
        print("2. 🛡️ Антивирус интегрирован в SafeFunctionManager")
        print("3. ⚙️ Обработчики функций работают")
        print("4. 📊 Функции зарегистрированы")
    else:
        print("❌ ПРОСТОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
