#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция одной функции с использованием 16-этапного алгоритма
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from complete_16_stage_algorithm import Complete16StageAlgorithm

def integrate_function(function_path):
    """Интегрирует одну функцию"""
    print(f"🚀 ИНТЕГРАЦИЯ ФУНКЦИИ: {function_path}")
    print("=" * 80)
    
    # Создание экземпляра алгоритма
    algorithm = Complete16StageAlgorithm()
    
    # Выполнение интеграции
    result = algorithm.run_complete_16_stage_integration(function_path)
    
    # Вывод результата
    print("\n📊 РЕЗУЛЬТАТ ИНТЕГРАЦИИ:")
    print(f"✅ Успех: {result['success']}")
    print(f"🆔 Зарегистрированные функции: {len(result['registered_functions'])}")
    print(f"⭐ Качество: {result['quality_score']:.1f}/100")
    print(f"🔍 SFM верификация: {result['sfm_verification']}")
    print(f"📋 Этапов выполнено: {len(result['steps_completed'])}/16")
    
    if result['errors']:
        print(f"❌ Ошибки: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   - {error}")
    
    if result['warnings']:
        print(f"⚠️ Предупреждения: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    return result

if __name__ == "__main__":
    # Интеграция NetworkSecurityBot
    function_path = "security/bots/network_security_bot.py"
    result = integrate_function(function_path)
    
    if result['success']:
        print(f"\n🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"✅ Зарегистрированы функции: {result['registered_functions']}")
    else:
        print(f"\n❌ ИНТЕГРАЦИЯ НЕ УДАЛАСЬ!")
        print(f"Ошибки: {result['errors']}")