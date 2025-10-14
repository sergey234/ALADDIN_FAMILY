#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция TrustScoring с SafeFunctionManager
"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel

def integrate_trust_scoring() -> bool:
    """Интеграция TrustScoring с SafeFunctionManager"""
    print("🚀 ИНТЕГРАЦИЯ TRUSTSCORING:")
    
    manager = SafeFunctionManager()
    manager.initialize()
    
    print("📝 Регистрируем TrustScoring...")
    success = manager.register_function(
        function_id="trust_scoring",
        name="TrustScoring",
        description="Система оценки доверия для семей",
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
    
    print("\n🎉 FUNCTION_26 ЗАВЕРШЕН!")
    return success

if __name__ == "__main__":
    success = integrate_trust_scoring()
    sys.exit(0 if success else 1)