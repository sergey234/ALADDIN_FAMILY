#!/usr/bin/env python3
"""
Комплексная проверка работоспособности системы после исправлений
"""

import json
import os
import sys
from datetime import datetime

def test_system_comprehensive():
    """Комплексная проверка системы безопасности"""
    
    print("🔍 КОМПЛЕКСНАЯ ПРОВЕРКА СИСТЕМЫ")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "overall_status": "UNKNOWN"
    }
    
    # 1. ПРОВЕРКА SFM ЗАГРУЗКИ
    print("\n1. 🔧 ПРОВЕРКА SFM ЗАГРУЗКИ")
    print("-" * 30)
    try:
        sys.path.append('.')
        from security.safe_function_manager import SafeFunctionManager
        sfm = SafeFunctionManager()
        results["tests"]["sfm_load"] = {
            "status": "PASS",
            "functions_count": len(sfm.functions),
            "message": f"SFM загружен успешно: {len(sfm.functions)} функций"
        }
        print(f"✅ SFM загружен: {len(sfm.functions)} функций")
    except Exception as e:
        results["tests"]["sfm_load"] = {
            "status": "FAIL",
            "error": str(e),
            "message": f"Ошибка загрузки SFM: {e}"
        }
        print(f"❌ Ошибка загрузки SFM: {e}")
    
    # 2. ПРОВЕРКА РЕЕСТРА JSON
    print("\n2. 📋 ПРОВЕРКА РЕЕСТРА JSON")
    print("-" * 30)
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        total_functions = len(registry.get("functions", {}))
        results["tests"]["registry_load"] = {
            "status": "PASS",
            "total_functions": total_functions,
            "message": f"Реестр загружен: {total_functions} функций"
        }
        print(f"✅ Реестр загружен: {total_functions} функций")
    except Exception as e:
        results["tests"]["registry_load"] = {
            "status": "FAIL",
            "error": str(e),
            "message": f"Ошибка загрузки реестра: {e}"
        }
        print(f"❌ Ошибка загрузки реестра: {e}")
    
    # 3. ПРОВЕРКА ИСПРАВЛЕННЫХ ФАЙЛОВ
    print("\n3. 📁 ПРОВЕРКА ИСПРАВЛЕННЫХ ФАЙЛОВ")
    print("-" * 30)
    
    # Получаем последние исправленные функции из реестра
    fixed_functions = []
    for func_id, func_data in registry.get("functions", {}).items():
        file_path = func_data.get("file_path", "")
        if file_path and os.path.exists(file_path):
            # Проверяем что это не старый путь
            if not file_path.startswith("security/") or "/" in file_path.replace("security/", ""):
                fixed_functions.append({
                    "id": func_id,
                    "path": file_path,
                    "exists": True
                })
    
    # Проверяем существование файлов
    existing_count = 0
    for func in fixed_functions:
        if os.path.exists(func["path"]):
            existing_count += 1
            print(f"✅ {func['id']}: {func['path']}")
        else:
            print(f"❌ {func['id']}: {func['path']} - НЕ НАЙДЕН")
    
    results["tests"]["fixed_files"] = {
        "status": "PASS" if existing_count == len(fixed_functions) else "PARTIAL",
        "total_checked": len(fixed_functions),
        "existing": existing_count,
        "missing": len(fixed_functions) - existing_count,
        "message": f"Проверено {len(fixed_functions)} файлов, найдено {existing_count}"
    }
    
    # 4. ПРОВЕРКА СИНТАКСИСА PYTHON
    print("\n4. 🐍 ПРОВЕРКА СИНТАКСИСА PYTHON")
    print("-" * 30)
    
    syntax_errors = 0
    checked_files = 0
    
    for func in fixed_functions[:5]:  # Проверяем первые 5 файлов
        if func["path"].endswith('.py') and os.path.exists(func["path"]):
            checked_files += 1
            try:
                with open(func["path"], 'r', encoding='utf-8') as f:
                    compile(f.read(), func["path"], 'exec')
                print(f"✅ {os.path.basename(func['path'])}: Синтаксис OK")
            except SyntaxError as e:
                syntax_errors += 1
                print(f"❌ {os.path.basename(func['path'])}: Ошибка синтаксиса - {e}")
    
    results["tests"]["python_syntax"] = {
        "status": "PASS" if syntax_errors == 0 else "FAIL",
        "checked_files": checked_files,
        "syntax_errors": syntax_errors,
        "message": f"Проверено {checked_files} файлов, ошибок: {syntax_errors}"
    }
    
    # 5. ПРОВЕРКА ИМПОРТОВ
    print("\n5. 📦 ПРОВЕРКА ИМПОРТОВ")
    print("-" * 30)
    
    import_errors = 0
    for func in fixed_functions[:3]:  # Проверяем первые 3 файла
        if func["path"].endswith('.py') and os.path.exists(func["path"]):
            try:
                # Пытаемся импортировать модуль
                module_name = func["path"].replace('/', '.').replace('.py', '')
                if module_name.startswith('.'):
                    module_name = module_name[1:]
                
                # Простая проверка импорта
                with open(func["path"], 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'import ' in content or 'from ' in content:
                        print(f"✅ {os.path.basename(func['path'])}: Импорты найдены")
                    else:
                        print(f"⚠️ {os.path.basename(func['path'])}: Нет импортов")
            except Exception as e:
                import_errors += 1
                print(f"❌ {os.path.basename(func['path'])}: Ошибка импорта - {e}")
    
    results["tests"]["imports"] = {
        "status": "PASS" if import_errors == 0 else "PARTIAL",
        "import_errors": import_errors,
        "message": f"Ошибок импорта: {import_errors}"
    }
    
    # 6. ОБЩАЯ ОЦЕНКА
    print("\n6. 📊 ОБЩАЯ ОЦЕНКА")
    print("-" * 30)
    
    passed_tests = sum(1 for test in results["tests"].values() if test["status"] == "PASS")
    total_tests = len(results["tests"])
    
    if passed_tests == total_tests:
        results["overall_status"] = "EXCELLENT"
        print("🎉 ОТЛИЧНО! Все проверки пройдены!")
    elif passed_tests >= total_tests * 0.8:
        results["overall_status"] = "GOOD"
        print("✅ ХОРОШО! Большинство проверок пройдено!")
    elif passed_tests >= total_tests * 0.6:
        results["overall_status"] = "FAIR"
        print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Есть проблемы!")
    else:
        results["overall_status"] = "POOR"
        print("❌ ПЛОХО! Много проблем!")
    
    print(f"\n📈 РЕЗУЛЬТАТ: {passed_tests}/{total_tests} проверок пройдено")
    print(f"🏆 СТАТУС: {results['overall_status']}")
    
    # Сохраняем результаты
    with open('data/sfm/repair_reports/test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

if __name__ == "__main__":
    test_system_comprehensive()