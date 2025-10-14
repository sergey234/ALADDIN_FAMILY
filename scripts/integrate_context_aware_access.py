#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция ContextAwareAccess с SafeFunctionManager
"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel

def integrate_context_aware_access() -> bool:
    """Интеграция ContextAwareAccess с SafeFunctionManager"""
    print("🚀 ИНТЕГРАЦИЯ CONTEXTAWARACCESS:")
    
    manager = SafeFunctionManager()
    manager.initialize()
    
    print("📝 Регистрируем ContextAwareAccess...")
    success = manager.register_function(
        function_id="context_aware_access",
        name="ContextAwareAccess",
        description="Контекстно-зависимый доступ для семей",
        function_type="preliminary",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=False
    )
    print(f"   Результат: {'✅ УСПЕШНО' if success else '❌ ОШИБКА'}")
    
    print("\n📊 СТАТУС СИСТЕМЫ:")
    status = manager.get_status()
    print(f"Всего функций: {status.get('total_functions', 0)}")
    print(f"Включено: {status.get('functions_enabled', 0)}")
    print(f"Отключено: {status.get('functions_disabled', 0)}")
    
    # Статистика по типам
    types_stats = status.get('functions_by_type', {})
    if types_stats:
        print("По типам:")
        for func_type, count in types_stats.items():
            print(f"  {func_type}: {count}")
    
    print("\n🎉 FUNCTION_27 ЗАВЕРШЕН!")
    return success

if __name__ == "__main__":
    success = integrate_context_aware_access()
    sys.exit(0 if success else 1)