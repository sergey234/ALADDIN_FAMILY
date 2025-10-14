#!/usr/bin/env python3
"""
Проверка количества экземпляров SafeFunctionManager в системе
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager

def check_sfm_instances():
    """Проверяем количество экземпляров SFM"""
    print("=" * 80)
    print("🔍 ПРОВЕРКА ЭКЗЕМПЛЯРОВ SAFE FUNCTION MANAGER")
    print("=" * 80)
    
    try:
        # Создаем первый SFM
        print("1. Создание первого SFM...")
        sfm1 = SafeFunctionManager("SFM1")
        functions1 = sfm1.get_all_functions_status()
        print(f"   ✅ SFM1 создан, функций: {len(functions1)}")
        
        # Создаем второй SFM
        print("2. Создание второго SFM...")
        sfm2 = SafeFunctionManager("SFM2")
        functions2 = sfm2.get_all_functions_status()
        print(f"   ✅ SFM2 создан, функций: {len(functions2)}")
        
        # Создаем третий SFM
        print("3. Создание третьего SFM...")
        sfm3 = SafeFunctionManager("SFM3")
        functions3 = sfm3.get_all_functions_status()
        print(f"   ✅ SFM3 создан, функций: {len(functions3)}")
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"   SFM1: {len(functions1)} функций")
        print(f"   SFM2: {len(functions2)} функций")
        print(f"   SFM3: {len(functions3)} функций")
        
        # Проверяем, это разные экземпляры?
        print(f"\n🔍 ПРОВЕРКА ЭКЗЕМПЛЯРОВ:")
        print(f"   SFM1 == SFM2: {sfm1 is sfm2}")
        print(f"   SFM1 == SFM3: {sfm1 is sfm3}")
        print(f"   SFM2 == SFM3: {sfm2 is sfm3}")
        
        # Проверяем ID
        print(f"\n🆔 ID ЭКЗЕМПЛЯРОВ:")
        print(f"   SFM1 ID: {id(sfm1)}")
        print(f"   SFM2 ID: {id(sfm2)}")
        print(f"   SFM3 ID: {id(sfm3)}")
        
        print("\n" + "=" * 80)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sfm_instances()