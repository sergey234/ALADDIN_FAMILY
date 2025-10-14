#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест асинхронной функциональности
"""

import sys
import asyncio
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.scaling.auto_scaling_engine import AutoScalingEngine

async def test_simple_async():
    """Простой тест асинхронной функциональности"""
    print("=== ПРОСТОЙ ТЕСТ АСИНХРОННОЙ ФУНКЦИОНАЛЬНОСТИ ===")
    
    try:
        # Тест асинхронного контекстного менеджера
        print("🔧 Тестирование асинхронного контекстного менеджера...")
        
        async with AutoScalingEngine("SimpleAsyncTest") as engine:
            print("   ✅ Асинхронный контекстный менеджер - работает")
            
            # Простой тест
            status = engine.get_engine_status()
            print(f"   ✅ Статус: {status.get('status', 'unknown')}")
        
        print("   ✅ Асинхронный контекстный менеджер - завершен без ошибок")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в простом тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_simple_async())
    print(f"\n🎯 РЕЗУЛЬТАТ: {'УСПЕХ' if result else 'ПРОВАЛ'}")