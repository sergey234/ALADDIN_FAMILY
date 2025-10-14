#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка всех Preliminary функций
"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel

def check_all_preliminary_functions() -> bool:
    """Проверка всех preliminary функций"""
    print("🔍 ПРОВЕРКА ВСЕХ PRELIMINARY ФУНКЦИЙ:")
    
    manager = SafeFunctionManager()
    manager.initialize()
    
    success = True
    
    functions_to_register = [
        ('zero_trust_service', 'ZeroTrustService', 'Упрощенная Zero Trust архитектура для семей'),
        ('mfa_service', 'MFAService', 'Многофакторная аутентификация для семей'),
        ('behavioral_analysis', 'BehavioralAnalysis', 'Анализ поведения пользователей для выявления аномалий'),
        ('risk_assessment_service', 'RiskAssessmentService', 'Оценка рисков безопасности'),
        ('policy_engine', 'PolicyEngine', 'Движок политик безопасности'),
        ('trust_scoring', 'TrustScoring', 'Система оценки доверия для семей'),
        ('context_aware_access', 'ContextAwareAccess', 'Контекстно-зависимый доступ для семей')
    ]
    
    for func_id, name, desc in functions_to_register:
        print(f"📝 Регистрируем {name}...")
        result = manager.register_function(
            function_id=func_id,
            name=name,
            description=desc,
            function_type="preliminary",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False
        )
        print(f"   Результат: {'✅ УСПЕШНО' if result else '❌ ОШИБКА'}")
        if not result: success = False
    
    print("\n📊 ФИНАЛЬНЫЙ СТАТУС СИСТЕМЫ:")
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
    
    print("\n🎉 УРОВЕНЬ 1 ПРОГРЕСС:")
    print(f"Preliminary функции: {types_stats.get('preliminary', 0)}/7")
    
    return success

if __name__ == "__main__":
    success = check_all_preliminary_functions()
    sys.exit(0 if success else 1)