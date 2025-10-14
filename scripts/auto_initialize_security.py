#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ БЕЗОПАСНОСТИ ДЛЯ ПРОДАКШЕНА
Запускается при каждом старте системы для гарантии безопасности
"""

import sys
import os
import time
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def auto_initialize_security():
    """Автоматическая инициализация всех компонентов безопасности"""
    
    print("🛡️ АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    try:
        # 1. Инициализация SafeFunctionManager
        from security.safe_function_manager import SafeFunctionManager
        sfm = SafeFunctionManager()
        print("✅ SafeFunctionManager инициализирован")
        
        # 2. Критически важные компоненты безопасности
        critical_components = [
            "scripts/integrate_anti_fraud_master_ai.py",
            "scripts/integrate_advanced_monitoring_simple.py", 
            "scripts/integrate_external_apis_simple.py",
            "scripts/integrate_high_priority_components.py"
        ]
        
        success_count = 0
        total_count = len(critical_components)
        
        for component in critical_components:
            try:
                print(f"🔧 Запуск {component}...")
                exec(open(component).read())
                success_count += 1
                print(f"✅ {component} выполнен успешно")
            except Exception as e:
                print(f"❌ Ошибка в {component}: {e}")
        
        # 3. Проверка результата
        print(f"\n📊 РЕЗУЛЬТАТ ИНИЦИАЛИЗАЦИИ:")
        print(f"   Успешно: {success_count}/{total_count}")
        print(f"   Успешность: {(success_count/total_count)*100:.1f}%")
        
        # 4. Сохранение статуса
        status = {
            "timestamp": datetime.now().isoformat(),
            "success_count": success_count,
            "total_count": total_count,
            "success_rate": (success_count/total_count)*100,
            "status": "SUCCESS" if success_count >= total_count * 0.8 else "PARTIAL"
        }
        
        with open("security_initialization_status.json", "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Статус сохранен в security_initialization_status.json")
        
        if success_count >= total_count * 0.8:
            print("🎉 БЕЗОПАСНОСТЬ АКТИВНА! Система готова к работе с пользователями")
            return True
        else:
            print("⚠️ ЧАСТИЧНАЯ ИНИЦИАЛИЗАЦИЯ! Требуется проверка")
            return False
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА ИНИЦИАЛИЗАЦИИ: {e}")
        return False

if __name__ == "__main__":
    success = auto_initialize_security()
    sys.exit(0 if success else 1)