#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Script для отключения 12 функций в спящий режим
Безопасное отключение функций для ускорения разработки
"""

import sys
import os
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus


def main():
    """Главная функция отключения"""
    print("🚀 ОТКЛЮЧЕНИЕ 12 ФУНКЦИЙ В СПЯЩИЙ РЕЖИМ")
    print("=" * 50)
    
    try:
        # Инициализация менеджера
        print("🔧 Инициализация SafeFunctionManager...")
        manager = SafeFunctionManager()
        manager.initialize()
        print("✅ SafeFunctionManager готов")
        
        # Список функций для отключения
        functions_to_disable = [
            "policy_engine",           # function_22
            "risk_assessment",         # function_23  
            "behavioral_analysis",     # function_24
            "mfa_service",            # function_25
            "zero_trust_service",     # function_26
            "trust_scoring",          # function_27
            "context_aware_access",   # function_28
            "service_mesh_manager",   # function_36
            "api_gateway_manager",    # function_37
            "redis_cache_manager",    # function_38
            "threat_detection_agent", # function_39
            "performance_optimization_agent" # function_40
        ]
        
        print("🎯 Отключаем {} функций...".format(len(functions_to_disable)))
        
        disabled_count = 0
        for func_id in functions_to_disable:
            try:
                success = manager.disable_function(func_id)
                if success:
                    print("✅ {} - отключен".format(func_id))
                    disabled_count += 1
                else:
                    print("⚠️ {} - не найден или уже отключен".format(func_id))
            except Exception as e:
                print("❌ {} - ошибка: {}".format(func_id, e))
        
        print("\n📊 РЕЗУЛЬТАТ: {}/{} функций отключено".format(disabled_count, len(functions_to_disable)))
        print("💤 Функции переведены в спящий режим для ускорения разработки")
        
        # Сохранение отчета
        report = """
# ОТЧЕТ ОБ ОТКЛЮЧЕНИИ ФУНКЦИЙ
Дата: {}
Отключено: {}/{} функций

Отключенные функции:
{}
""".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            disabled_count,
            len(functions_to_disable),
            '\n'.join("- {}".format(func) for func in functions_to_disable[:disabled_count])
        )
        
        report_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 
                                 'disable_report_{}.md'.format(datetime.now().strftime("%Y%m%d_%H%M%S")))
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("📄 Отчет сохранен: {}".format(report_path))
        print("🎉 ГОТОВО! Функции отключены безопасно")
        
    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: {}".format(e))
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)