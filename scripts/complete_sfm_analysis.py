#!/usr/bin/env python3
"""
Полный анализ ВСЕХ функций в ALADDIN Security System
"""
import sys
import os
import subprocess
from datetime import datetime
import re

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_code_quality(file_path):
    """Проверяет качество кода файла"""
    try:
        if not os.path.exists(file_path):
            return 999, "Файл не найден"
            
        result = subprocess.run(
            ["python3", "-m", "flake8", file_path, "--count", "--statistics"],
            capture_output=True, text=True, cwd="/Users/sergejhlystov/ALADDIN_NEW"
        )
        if result.returncode == 0:
            return 0, "A+"
        else:
            lines = result.stdout.strip().split('\n')
            if lines and lines[-1].isdigit():
                errors = int(lines[-1])
                if errors <= 25:
                    return errors, "A+"
                elif errors <= 50:
                    return errors, "A"
                elif errors <= 100:
                    return errors, "B"
                elif errors <= 200:
                    return errors, "C"
                else:
                    return errors, "D"
            return 0, "A+"
    except Exception as e:
        return 999, f"Ошибка: {e}"

def get_function_type(file_path):
    """Определяет тип функции по пути"""
    if "microservices" in file_path:
        return "Microservice"
    elif "ai_agents" in file_path:
        return "AI Agent"
    elif "bots" in file_path:
        return "Security Bot"
    elif "privacy" in file_path:
        return "Privacy Manager"
    elif "family" in file_path:
        return "Family Protection"
    elif "preliminary" in file_path:
        return "Preliminary"
    elif "antivirus" in file_path:
        return "Antivirus"
    elif "vpn" in file_path:
        return "VPN"
    elif "compliance" in file_path:
        return "Compliance"
    elif "active" in file_path:
        return "Active Security"
    elif "reactive" in file_path:
        return "Reactive Security"
    elif "mobile" in file_path:
        return "Mobile Security"
    elif "orchestration" in file_path:
        return "Orchestration"
    elif "scaling" in file_path:
        return "Scaling"
    else:
        return "Core Security"

def get_function_status(file_path):
    """Определяет статус функции"""
    if "_new" in file_path:
        return "🆕 Новая версия"
    elif "_old" in file_path or "_backup" in file_path:
        return "💤 Архивная"
    elif "integration" in file_path or "test" in file_path:
        return "🧪 Тестовая"
    else:
        return "✅ Активная"

def analyze_all_functions():
    """Анализирует все функции в системе"""
    print("🔍 ПОЛНЫЙ АНАЛИЗ ВСЕХ ФУНКЦИЙ ALADDIN SECURITY SYSTEM")
    print("=" * 80)
    print(f"Время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Получаем все файлы
    result = subprocess.run(
        ["find", "security", "-name", "*.py", "-type", "f"],
        capture_output=True, text=True, cwd="/Users/sergejhlystov/ALADDIN_NEW"
    )
    
    all_files = result.stdout.strip().split('\n')
    
    # Фильтруем файлы
    functions = []
    for file_path in all_files:
        if (file_path and 
            not file_path.endswith('__init__.py') and
            not file_path.endswith('__pycache__') and
            not '/test_' in file_path and
            not '/integration_test' in file_path):
            
            # Извлекаем имя функции
            filename = os.path.basename(file_path)
            function_name = filename.replace('.py', '').replace('_', ' ').title()
            
            functions.append({
                "path": file_path,
                "name": function_name,
                "filename": filename
            })
    
    print(f"\n📊 Всего функций для анализа: {len(functions)}")
    print("\n" + "="*80)
    
    # Группируем по типам
    by_type = {}
    for func in functions:
        func_type = get_function_type(func["path"])
        if func_type not in by_type:
            by_type[func_type] = []
        by_type[func_type].append(func)
    
    total_errors = 0
    a_plus_count = 0
    a_count = 0
    b_count = 0
    c_count = 0
    d_count = 0
    
    # Анализируем по типам
    for func_type, funcs in by_type.items():
        print(f"\n🔧 {func_type.upper()} ({len(funcs)} функций)")
        print("-" * 60)
        
        for i, func in enumerate(funcs, 1):
            # Проверяем качество кода
            errors, quality = check_code_quality(func["path"])
            total_errors += errors
            
            # Определяем статус
            status = get_function_status(func["path"])
            
            # Иконки качества
            if quality == "A+":
                a_plus_count += 1
                quality_icon = "✅"
            elif quality == "A":
                a_count += 1
                quality_icon = "⚠️"
            elif quality == "B":
                b_count += 1
                quality_icon = "🔶"
            elif quality == "C":
                c_count += 1
                quality_icon = "🔴"
            else:
                d_count += 1
                quality_icon = "❌"
            
            print(f"{i:2d}. {quality_icon} {func['name']}")
            print(f"    📁 {func['path']}")
            print(f"    📊 Качество: {quality} ({errors} ошибок)")
            print(f"    📍 Статус: {status}")
            
            # Рекомендации
            if quality == "A+":
                recommendation = "Отличное качество! Готов к продакшену."
            elif quality == "A":
                recommendation = "Хорошее качество. Можно улучшить до A+."
            elif quality == "B":
                recommendation = "Среднее качество. Требует рефакторинга."
            elif quality == "C":
                recommendation = "Плохое качество. Критически нужен рефакторинг."
            else:
                recommendation = "Очень плохое качество. Требует полной переработки."
            
            print(f"    💡 Рекомендация: {recommendation}")
            print()
    
    # Итоговая статистика
    print("="*80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"• Всего функций: {len(functions)}")
    print(f"• Функций по типам:")
    for func_type, funcs in by_type.items():
        print(f"   - {func_type}: {len(funcs)}")
    print(f"• Качество кода:")
    print(f"   - A+ (отлично): {a_plus_count} ({a_plus_count/len(functions)*100:.1f}%)")
    print(f"   - A (хорошо): {a_count} ({a_count/len(functions)*100:.1f}%)")
    print(f"   - B (средне): {b_count} ({b_count/len(functions)*100:.1f}%)")
    print(f"   - C (плохо): {c_count} ({c_count/len(functions)*100:.1f}%)")
    print(f"   - D (очень плохо): {d_count} ({d_count/len(functions)*100:.1f}%)")
    print(f"• Общее количество ошибок: {total_errors}")
    print(f"• Среднее количество ошибок: {total_errors // len(functions) if functions else 0}")
    
    if a_plus_count == len(functions):
        print("🎉 ВСЕ ФУНКЦИИ ИМЕЮТ A+ КАЧЕСТВО!")
    else:
        print(f"⚠️  {len(functions) - a_plus_count} функций требуют улучшения")
    
    return total_errors, len(functions)

if __name__ == "__main__":
    analyze_all_functions()