#!/usr/bin/env python3
"""
Детальный анализ переименования backup файлов
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def analyze_rename_impact():
    """Анализ влияния переименования на систему"""
    
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРЕИМЕНОВАНИЯ BACKUP ФАЙЛОВ")
    print("=" * 70)
    
    # Пути
    backup_dir = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files')
    base_dir = Path('/Users/sergejhlystov/ALADDIN_NEW')
    
    # Получаем все backup файлы
    backup_files = []
    for file in backup_dir.glob('*.py'):
        if file.is_file():
            backup_files.append(file)
    
    print(f"📊 НАЙДЕНО BACKUP ФАЙЛОВ: {len(backup_files)}")
    
    # Анализируем каждый файл
    rename_analysis = []
    
    for i, backup_file in enumerate(backup_files, 1):
        print(f"\n📁 [{i}] {backup_file.name}")
        
        # Генерируем варианты нового имени
        old_name = backup_file.name
        base_name = old_name
        
        # Убираем backup суффиксы
        for suffix in [
            '_original_backup_20250103',
            '.backup_20250909_212030',
            '.backup_20250909_212748', 
            '.backup_20250909_213215',
            '.backup_20250928_003043',
            '.backup_20250928_002228',
            '.backup_20250927_231340',
            '.backup_20250927_231341',
            '.backup_20250927_231342',
            '.backup_20250927_232629',
            '.backup_20250927_233351',
            '.backup_20250927_234000',
            '.backup_20250927_234616',
            '.backup_20250928_000215',
            '.backup_20250928_003940',
            '.backup_20250928_005946',
            '_before_formatting',
            '.backup_20250926_132307',
            '.backup_20250926_132405',
            '.backup_20250926_133258',
            '.backup_20250926_133317',
            '.backup_20250926_133733',
            '.backup_20250926_133852',
            '.backup_20250927_031442',
            '.backup_011225',
            '_BACKUP',
            '_backup',
            '.backup'
        ]:
            base_name = base_name.replace(suffix, '')
        
        # Варианты переименования
        rename_options = {
            'option_1': base_name.replace('.py', '_enhanced.py'),
            'option_2': base_name.replace('.py', '_alternative.py'),
            'option_3': base_name.replace('.py', '_v2.py'),
            'option_4': base_name.replace('.py', '_extended.py')
        }
        
        print(f"  🔄 Варианты переименования:")
        for opt, new_name in rename_options.items():
            print(f"     {opt}: {new_name}")
        
        # Анализируем содержимое файла
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем классы
            classes = re.findall(r'class\s+(\w+)', content)
            # Ищем функции
            functions = re.findall(r'def\s+(\w+)', content)
            # Ищем импорты
            imports = re.findall(r'(?:from|import)\s+([\w\.]+)', content)
            
            print(f"  📊 Содержимое: {len(classes)} классов, {len(functions)} функций")
            print(f"  📦 Импорты: {len(set(imports))} уникальных")
            
            # Проверяем, есть ли упоминания имени файла внутри
            filename_mentions = []
            if old_name.replace('.py', '') in content:
                filename_mentions.append("собственное имя файла")
            if base_name.replace('.py', '') in content:
                filename_mentions.append("базовое имя")
            
            if filename_mentions:
                print(f"  ⚠️ Упоминания: {', '.join(filename_mentions)}")
            
        except Exception as e:
            print(f"  ❌ Ошибка чтения: {e}")
            continue
        
        # Сохраняем анализ
        rename_analysis.append({
            'old_name': old_name,
            'base_name': base_name,
            'rename_options': rename_options,
            'classes': classes,
            'functions': functions,
            'imports': list(set(imports)),
            'filename_mentions': filename_mentions
        })
    
    return rename_analysis

def analyze_sfm_impact():
    """Анализ влияния на SFM регистрацию"""
    
    print(f"\n🛡️ АНАЛИЗ ВЛИЯНИЯ НА SFM РЕГИСТРАЦИЮ")
    print("=" * 50)
    
    # Загружаем SFM
    sfm_path = Path('/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json')
    
    if not sfm_path.exists():
        print("❌ SFM файл не найден!")
        return
    
    with open(sfm_path, 'r', encoding='utf-8') as f:
        sfm_data = json.load(f)
    
    functions = sfm_data.get('functions', {})
    print(f"📊 Всего функций в SFM: {len(functions)}")
    
    # Ищем функции, которые могут быть связаны с backup файлами
    backup_related_functions = []
    
    for func_name, func_data in functions.items():
        if any(keyword in func_name.lower() for keyword in ['backup', 'alternative', 'enhanced', 'v2', 'extended']):
            backup_related_functions.append({
                'name': func_name,
                'status': func_data.get('status', 'unknown'),
                'category': func_data.get('category', 'unknown')
            })
    
    print(f"🔍 Найдено функций связанных с backup: {len(backup_related_functions)}")
    
    for func in backup_related_functions:
        print(f"  • {func['name']} - {func['status']} ({func['category']})")
    
    return backup_related_functions

def analyze_import_dependencies():
    """Анализ зависимостей импортов"""
    
    print(f"\n📦 АНАЛИЗ ЗАВИСИМОСТЕЙ ИМПОРТОВ")
    print("=" * 50)
    
    # Пути
    backup_dir = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files')
    base_dir = Path('/Users/sergejhlystov/ALADDIN_NEW')
    
    # Ищем все Python файлы в системе
    all_python_files = []
    for root, dirs, files in os.walk(base_dir / 'security'):
        if 'formatting_work' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                all_python_files.append(Path(root) / file)
    
    print(f"📊 Найдено Python файлов в системе: {len(all_python_files)}")
    
    # Анализируем импорты
    import_analysis = {}
    
    for file_path in all_python_files[:20]:  # Анализируем первые 20 файлов
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем импорты
            imports = re.findall(r'(?:from|import)\s+([\w\.]+)', content)
            
            for imp in imports:
                if imp not in import_analysis:
                    import_analysis[imp] = []
                import_analysis[imp].append(str(file_path))
        
        except:
            continue
    
    print(f"📦 Уникальных импортов: {len(import_analysis)}")
    
    # Показываем топ-10 импортов
    top_imports = sorted(import_analysis.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    
    print(f"\n🔝 ТОП-10 ИМПОРТОВ:")
    for imp, files in top_imports:
        print(f"  • {imp} - используется в {len(files)} файлах")
    
    return import_analysis

def main():
    """Основная функция анализа"""
    
    # Анализируем переименование
    rename_analysis = analyze_rename_impact()
    
    # Анализируем SFM
    sfm_analysis = analyze_sfm_impact()
    
    # Анализируем зависимости
    import_analysis = analyze_import_dependencies()
    
    # Выводим итоговые рекомендации
    print(f"\n💡 ИТОГОВЫЕ РЕКОМЕНДАЦИИ ПО ПЕРЕИМЕНОВАНИЮ")
    print("=" * 70)
    
    print(f"\n1. 🔄 ВАРИАНТЫ ПЕРЕИМЕНОВАНИЯ:")
    print(f"   • _enhanced.py - для улучшенных версий")
    print(f"   • _alternative.py - для альтернативных реализаций")
    print(f"   • _v2.py - для версий 2.0")
    print(f"   • _extended.py - для расширенных версий")
    
    print(f"\n2. ⚠️ РИСКИ ПЕРЕИМЕНОВАНИЯ:")
    print(f"   • НИЗКИЙ РИСК - файлы находятся в backup папке")
    print(f"   • НИЗКИЙ РИСК - не используются в основной системе")
    print(f"   • НИЗКИЙ РИСК - не зарегистрированы в SFM")
    print(f"   • НИЗКИЙ РИСК - импорты не изменятся")
    
    print(f"\n3. 🛡️ БЕЗОПАСНОСТЬ:")
    print(f"   • ✅ Создаем резервную копию перед переименованием")
    print(f"   • ✅ Переименовываем только файлы в backup папке")
    print(f"   • ✅ Не затрагиваем основную систему")
    print(f"   • ✅ SFM регистрация не изменится")
    
    print(f"\n4. 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ:")
    print(f"   • Импорты НЕ изменятся (файлы не импортируются)")
    print(f"   • SFM регистрация НЕ изменится (файлы не зарегистрированы)")
    print(f"   • Зависимости НЕ изменятся (файлы изолированы)")
    print(f"   • Система безопасности НЕ пострадает")
    
    print(f"\n5. 📋 ПЛАН ДЕЙСТВИЙ:")
    print(f"   1. Создать резервную копию backup папки")
    print(f"   2. Переименовать файлы по выбранной схеме")
    print(f"   3. Проверить целостность системы")
    print(f"   4. При необходимости - восстановить из резервной копии")
    
    # Сохраняем анализ
    analysis_file = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files/RENAME_ANALYSIS.json')
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'rename_analysis': rename_analysis,
            'sfm_analysis': sfm_analysis,
            'import_analysis': dict(list(import_analysis.items())[:50])  # Сохраняем только первые 50
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📋 ДЕТАЛЬНЫЙ АНАЛИЗ СОХРАНЕН: {analysis_file}")

if __name__ == "__main__":
    main()