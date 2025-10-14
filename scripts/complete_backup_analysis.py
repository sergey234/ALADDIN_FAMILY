#!/usr/bin/env python3
"""
Полный анализ ВСЕХ backup файлов включая повторения
"""

import os
import json
import ast
import difflib
from pathlib import Path
from datetime import datetime

def analyze_file_structure(file_path):
    """Анализ структуры файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсинг AST
        tree = ast.parse(content)
        
        # Извлечение информации
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(f"{node.module or ''}.{', '.join([alias.name for alias in node.names])}")
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'lines': len(content.splitlines()),
            'size': len(content)
        }
    except Exception as e:
        return {'error': str(e)}

def compare_files(backup_path, original_path):
    """Сравнение двух файлов"""
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(original_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Анализ структуры
        backup_structure = analyze_file_structure(backup_path)
        original_structure = analyze_file_structure(original_path)
        
        # Сравнение классов
        backup_classes = {c['name']: c for c in backup_structure.get('classes', [])}
        original_classes = {c['name']: c for c in original_structure.get('classes', [])}
        
        class_comparison = {
            'backup_only': [name for name in backup_classes if name not in original_classes],
            'original_only': [name for name in original_classes if name not in backup_classes],
            'common': [name for name in backup_classes if name in original_classes]
        }
        
        # Сравнение функций
        backup_functions = {f['name']: f for f in backup_structure.get('functions', [])}
        original_functions = {f['name']: f for f in original_structure.get('functions', [])}
        
        function_comparison = {
            'backup_only': [name for name in backup_functions if name not in original_functions],
            'original_only': [name for name in original_functions if name not in backup_functions],
            'common': [name for name in backup_functions if name in original_functions]
        }
        
        # Сравнение импортов
        backup_imports = set(backup_structure.get('imports', []))
        original_imports = set(original_structure.get('imports', []))
        
        import_comparison = {
            'backup_only': list(backup_imports - original_imports),
            'original_only': list(original_imports - backup_imports),
            'common': list(backup_imports & original_imports)
        }
        
        # Размеры файлов
        size_comparison = {
            'backup_size': backup_structure.get('size', 0),
            'original_size': original_structure.get('size', 0),
            'backup_lines': backup_structure.get('lines', 0),
            'original_lines': original_structure.get('lines', 0)
        }
        
        # Процент различий
        diff_ratio = 0
        if original_content:
            diff_ratio = len(list(difflib.unified_diff(
                original_content.splitlines(keepends=True),
                backup_content.splitlines(keepends=True),
                fromfile='original',
                tofile='backup'
            ))) / len(original_content.splitlines()) * 100
        
        return {
            'class_comparison': class_comparison,
            'function_comparison': function_comparison,
            'import_comparison': import_comparison,
            'size_comparison': size_comparison,
            'diff_ratio': diff_ratio,
            'backup_structure': backup_structure,
            'original_structure': original_structure
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_all_backups():
    """Анализ всех backup файлов"""
    print("🔍 ПОЛНЫЙ АНАЛИЗ ВСЕХ BACKUP ФАЙЛОВ")
    print("=" * 80)
    
    # Пути
    backup_dir = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files')
    base_dir = Path('/Users/sergejhlystov/ALADDIN_NEW')
    
    # Получаем все backup файлы
    backup_files = []
    for file in backup_dir.glob('*.py'):
        if file.is_file():
            backup_files.append(file)
    
    # Сортируем по размеру
    backup_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    results = []
    duplicates_analysis = {}
    
    for i, backup_file in enumerate(backup_files, 1):
        print(f"\n📁 [{i}/{len(backup_files)}] Анализ: {backup_file.name}")
        
        # Очищаем имя от backup суффиксов
        original_name = backup_file.name
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
            original_name = original_name.replace(suffix, '')
        
        # Ищем оригинал
        original_path = None
        for root, dirs, files in os.walk(base_dir / 'security'):
            for file in files:
                if file == original_name:
                    original_path = Path(root) / file
                    break
            if original_path:
                break
        
        if not original_path:
            print(f"  ❌ Оригинал не найден: {original_name}")
            continue
        
        print(f"  🔍 Сравниваем с: {original_path.name}")
        
        # Сравниваем файлы
        comparison = compare_files(backup_file, original_path)
        
        if 'error' in comparison:
            print(f"  ❌ Ошибка сравнения: {comparison['error']}")
            continue
        
        # Анализируем дубликаты
        base_name = original_name.replace('.py', '')
        if base_name not in duplicates_analysis:
            duplicates_analysis[base_name] = []
        
        duplicates_analysis[base_name].append({
            'backup_file': backup_file.name,
            'backup_size': comparison['size_comparison']['backup_size'],
            'original_size': comparison['size_comparison']['original_size'],
            'diff_ratio': comparison['diff_ratio']
        })
        
        # Сохраняем результат
        result = {
            'backup_file': str(backup_file),
            'original_file': str(original_path),
            'backup_name': backup_file.name,
            'original_name': original_path.name,
            'comparison': comparison
        }
        results.append(result)
        
        # Выводим краткий результат
        print(f"  📊 Размер: backup {comparison['size_comparison']['backup_size']:,} vs original {comparison['size_comparison']['original_size']:,}")
        print(f"  📈 Различия: {comparison['diff_ratio']:.1f}%")
    
    # Анализ дубликатов
    print(f"\n🔄 АНАЛИЗ ДУБЛИКАТОВ")
    print("=" * 80)
    
    for base_name, duplicates in duplicates_analysis.items():
        if len(duplicates) > 1:
            print(f"\n📁 {base_name} - {len(duplicates)} версий:")
            for dup in duplicates:
                print(f"  • {dup['backup_file']} - {dup['backup_size']:,} байт (различия: {dup['diff_ratio']:.1f}%)")
            
            # Анализируем размеры
            sizes = [dup['backup_size'] for dup in duplicates]
            if len(set(sizes)) == 1:
                print(f"  🔍 ВСЕ ВЕРСИИ ИДЕНТИЧНЫ ПО РАЗМЕРУ - возможно это временные копии")
            else:
                print(f"  🔍 РАЗНЫЕ РАЗМЕРЫ - разные версии функциональности")
    
    # Сохраняем полный отчет
    report_file = backup_dir / f"COMPLETE_BACKUP_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_files': len(results),
            'duplicates_analysis': duplicates_analysis,
            'results': results
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📋 ПОЛНЫЙ ОТЧЕТ СОХРАНЕН: {report_file}")
    print(f"📊 ПРОАНАЛИЗИРОВАНО ФАЙЛОВ: {len(results)}")
    
    return results, duplicates_analysis

if __name__ == "__main__":
    analyze_all_backups()