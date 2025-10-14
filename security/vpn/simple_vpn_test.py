#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест VPN модулей
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест импорта модулей"""
    print("🔍 Тестирование импорта модулей...")
    
    try:
        from vpn_manager import VPNManager
        print("✅ VPN Manager импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта VPN Manager: {e}")
        return False
    
    try:
        from vpn_monitoring import VPNMonitoring
        print("✅ VPN Monitoring импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта VPN Monitoring: {e}")
        return False
    
    try:
        from vpn_analytics import VPNAnalytics
        print("✅ VPN Analytics импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта VPN Analytics: {e}")
        return False
    
    try:
        from vpn_integration import VPNIntegration
        print("✅ VPN Integration импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта VPN Integration: {e}")
        return False
    
    return True

def test_initialization():
    """Тест инициализации модулей"""
    print("\n🔧 Тестирование инициализации...")
    
    try:
        from vpn_manager import VPNManager
        manager = VPNManager()
        print("✅ VPN Manager инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации VPN Manager: {e}")
        return False
    
    try:
        from vpn_monitoring import VPNMonitoring
        monitoring = VPNMonitoring()
        print("✅ VPN Monitoring инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации VPN Monitoring: {e}")
        return False
    
    try:
        from vpn_analytics import VPNAnalytics
        analytics = VPNAnalytics()
        print("✅ VPN Analytics инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации VPN Analytics: {e}")
        return False
    
    try:
        from vpn_integration import VPNIntegration
        integration = VPNIntegration()
        print("✅ VPN Integration инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации VPN Integration: {e}")
        return False
    
    return True

async def test_async_functions():
    """Тест асинхронных функций"""
    print("\n⚡ Тестирование асинхронных функций...")
    
    try:
        from vpn_analytics import VPNAnalytics
        analytics = VPNAnalytics()
        
        # Добавляем тестовые данные
        analytics.add_data_point("test_metric", 100.0, user_id="test_user")
        
        # Тестируем отчет
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        
        report = await analytics.get_usage_report(start_date, end_date)
        print("✅ VPN Analytics отчет сгенерирован")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования VPN Analytics: {e}")
        return False
    
    try:
        from vpn_integration import VPNIntegration, EventType
        integration = VPNIntegration()
        
        # Тестируем создание события
        event_id = await integration.emit_event(
            EventType.USER_LOGIN,
            {"username": "testuser"},
            user_id="test_user"
        )
        print("✅ VPN Integration событие создано")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования VPN Integration: {e}")
        return False
    
    return True

def test_file_sizes():
    """Тест размеров файлов"""
    print("\n📊 Проверка размеров файлов...")
    
    files = [
        "vpn_manager.py",
        "vpn_monitoring.py", 
        "vpn_analytics.py",
        "vpn_integration.py"
    ]
    
    total_size = 0
    for file in files:
        try:
            size = Path(file).stat().st_size
            total_size += size
            print(f"✅ {file}: {size:,} байт")
        except Exception as e:
            print(f"❌ Ошибка чтения {file}: {e}")
            return False
    
    print(f"📈 Общий размер VPN модулей: {total_size:,} байт")
    return True

def main():
    """Главная функция тестирования"""
    print("🧪 ПРОСТОЕ ТЕСТИРОВАНИЕ VPN МОДУЛЕЙ")
    print("=" * 50)
    
    tests = [
        ("Импорт модулей", test_imports),
        ("Инициализация", test_initialization),
        ("Размеры файлов", test_file_sizes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - ПРОЙДЕН")
        else:
            print(f"❌ {test_name} - ПРОВАЛЕН")
    
    # Тест асинхронных функций
    print(f"\n🔍 Асинхронные функции...")
    try:
        result = asyncio.run(test_async_functions())
        if result:
            passed += 1
            print("✅ Асинхронные функции - ПРОЙДЕН")
        else:
            print("❌ Асинхронные функции - ПРОВАЛЕН")
    except Exception as e:
        print(f"❌ Ошибка тестирования асинхронных функций: {e}")
    
    total += 1
    
    # Итоговый результат
    success_rate = (passed / total) * 100
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🏆 ОТЛИЧНО! VPN модули работают!")
    elif success_rate >= 60:
        print("✅ ХОРОШО! VPN модули в основном работают!")
    else:
        print("⚠️  ТРЕБУЕТСЯ ДОРАБОТКА!")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
