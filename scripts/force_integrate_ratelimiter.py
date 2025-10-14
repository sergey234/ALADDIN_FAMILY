#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Принудительная интеграция RateLimiter в SFM
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager
import importlib.util

def force_integrate_ratelimiter():
    """Принудительно интегрируем RateLimiter в SFM"""
    
    print("🚀 ПРИНУДИТЕЛЬНАЯ ИНТЕГРАЦИЯ RateLimiter")
    print("=" * 50)
    
    # 1. Загружаем SFM
    sfm = SafeFunctionManager()
    print(f"📊 SFM загружен: {len(sfm.functions)} функций")
    
    # 2. Загружаем модуль RateLimiter
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/microservices/rate_limiter.py'
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return False
    
    print(f"📁 Загружаем файл: {file_path}")
    
    try:
        spec = importlib.util.spec_from_file_location("rate_limiter", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Модуль загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки модуля: {e}")
        return False
    
    # 3. Находим все классы в модуле
    classes = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and not name.startswith('_'):
            classes.append(name)
    
    print(f"📋 Найдено классов: {len(classes)}")
    for cls in classes:
        print(f"   - {cls}")
    
    # 4. Регистрируем каждый класс в SFM
    registered_count = 0
    
    for cls_name in classes:
        try:
            # Создаем ID функции
            func_id = f"microservice_{cls_name.lower()}"
            
            # Регистрируем функцию
            sfm.register_function(
                function_id=func_id,
                name=cls_name,
                description=f"Компонент {cls_name}",
                function_type="microservice",
                security_level="medium",
                is_critical=True
            )
            
            # Создаем обработчик
            sfm.function_handlers[func_id] = {
                'type': 'function',
                'function_name': 'safe_handler',
                'module': 'scripts.complete_16_stage_algorithm'
            }
            
            registered_count += 1
            print(f"✅ Зарегистрирован: {cls_name} -> {func_id}")
            
        except Exception as e:
            print(f"❌ Ошибка регистрации {cls_name}: {e}")
    
    # 5. Сохраняем изменения
    try:
        sfm._save_functions()
        print(f"💾 Изменения сохранены: {registered_count} функций")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False
    
    # 6. Проверяем результат
    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА:")
    print("=" * 30)
    
    rate_limiter_found = False
    for func_id, func in sfm.functions.items():
        if 'ratelimiter' in func_id.lower() or 'rate_limiter' in func_id.lower():
            print(f"✅ Найден: {func_id} -> {func.name}")
            rate_limiter_found = True
    
    if rate_limiter_found:
        print(f"\n🎯 УСПЕХ! RateLimiter интегрирован в SFM!")
        print(f"📊 Всего функций в SFM: {len(sfm.functions)}")
        return True
    else:
        print(f"\n❌ ОШИБКА! RateLimiter не найден в SFM!")
        return False

if __name__ == "__main__":
    success = force_integrate_ratelimiter()
    if success:
        print("\n🚀 ГОТОВО! RateLimiter успешно интегрирован!")
    else:
        print("\n💥 ОШИБКА! Интеграция не удалась!")
        sys.exit(1)