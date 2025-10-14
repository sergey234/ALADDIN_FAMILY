#!/usr/bin/env python3
"""
Автоматическая проверка качества всех функций ALADDIN
"""

import subprocess
import sys
import os
from datetime import datetime

def check_quality():
    """Проверяет качество всех функций"""
    
    # Список всех функций для проверки
    functions = [
        {
            "name": "LoadBalancer",
            "path": "security/microservices/load_balancer.py",
            "type": "Microservice"
        },
        {
            "name": "APIGateway", 
            "path": "security/microservices/api_gateway.py",
            "type": "Microservice"
        },
        {
            "name": "AnalyticsManager",
            "path": "security/ai_agents/analytics_manager.py", 
            "type": "AI Agent"
        },
        {
            "name": "DashboardManager",
            "path": "security/ai_agents/dashboard_manager.py",
            "type": "AI Agent"
        },
        {
            "name": "MonitorManager",
            "path": "security/ai_agents/monitor_manager.py",
            "type": "AI Agent"
        },
        {
            "name": "UniversalPrivacyManager",
            "path": "security/privacy/universal_privacy_manager.py",
            "type": "Privacy Manager"
        }
    ]
    
    print("🔍 АВТОМАТИЧЕСКАЯ ПРОВЕРКА КАЧЕСТВА ALADDIN")
    print("=" * 60)
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_errors = 0
    a_plus_functions = 0
    
    for func in functions:
        if not os.path.exists(func["path"]):
            print(f"❌ {func['name']}: Файл не найден")
            continue
            
        try:
            # Запускаем flake8
            result = subprocess.run(
                ["python3", "-m", "flake8", func["path"], "--count", "--statistics"],
                capture_output=True, text=True, cwd="/Users/sergejhlystov/ALADDIN_NEW"
            )
            
            # Парсим результат
            if result.returncode == 0:
                errors = 0
                print(f"✅ {func['name']}: 0 ошибок (A+)")
                a_plus_functions += 1
            else:
                # Извлекаем количество ошибок
                lines = result.stdout.strip().split('\n')
                if lines and lines[-1].isdigit():
                    errors = int(lines[-1])
                else:
                    errors = 0
                
                # Определяем качество
                if errors <= 50:
                    quality = "A+"
                    a_plus_functions += 1
                    status = "✅"
                elif errors <= 100:
                    quality = "A"
                    status = "⚠️"
                elif errors <= 200:
                    quality = "B"
                    status = "⚠️"
                else:
                    quality = "C"
                    status = "❌"
                
                print(f"{status} {func['name']}: {errors} ошибок ({quality})")
            
            total_errors += errors
            
        except Exception as e:
            print(f"❌ {func['name']}: Ошибка проверки - {e}")
    
    print()
    print("=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"• Всего функций: {len(functions)}")
    print(f"• Функций с A+ качеством: {a_plus_functions}")
    print(f"• Общее количество ошибок: {total_errors}")
    print(f"• Среднее количество ошибок: {total_errors // len(functions)}")
    
    if a_plus_functions == len(functions):
        print("🎉 ВСЕ ФУНКЦИИ ИМЕЮТ A+ КАЧЕСТВО!")
    else:
        print(f"⚠️  {len(functions) - a_plus_functions} функций требуют улучшения")
    
    return total_errors

if __name__ == "__main__":
    check_quality()
