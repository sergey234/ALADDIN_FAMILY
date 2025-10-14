#!/usr/bin/env python3
"""
Безопасное переименование backup файлов с проверкой зависимостей
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

def analyze_dependencies(file_path):
    """Анализ зависимостей файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем импорты
        imports = []
        import_patterns = [
            r'from\s+([\w\.]+)\s+import',
            r'import\s+([\w\.]+)',
            r'from\s+([\w\.]+)\s+import\s+\*'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        # Ищем упоминания имени файла
        filename = Path(file_path).stem
        filename_mentions = []
        
        # Ищем в строках
        string_patterns = [
            r'["\']([^"\']*' + re.escape(filename) + r'[^"\']*)["\']',
            r'["\']([^"\']*' + re.escape(filename.replace('_backup', '').replace('_BACKUP', '').replace('.backup', '')) + r'[^"\']*)["\']'
        ]
        
        for pattern in string_patterns:
            matches = re.findall(pattern, content)
            filename_mentions.extend(matches)
        
        return {
            'imports': list(set(imports)),
            'filename_mentions': list(set(filename_mentions)),
            'content_length': len(content)
        }
    except Exception as e:
        return {'error': str(e)}

def find_references_to_file(filename, search_dir):
    """Поиск ссылок на файл в других файлах"""
    references = []
    
    for root, dirs, files in os.walk(search_dir):
        if 'formatting_work' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if filename in content:
                        references.append({
                            'file': str(file_path),
                            'line': content.count(filename)
                        })
                except:
                    continue
    
    return references

def generate_new_name(backup_filename):
    """Генерация нового имени файла"""
    # Убираем backup суффиксы
    new_name = backup_filename
    
    # Список суффиксов для удаления
    suffixes_to_remove = [
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
    ]
    
    for suffix in suffixes_to_remove:
        new_name = new_name.replace(suffix, '')
    
    # Добавляем суффикс для альтернативных версий
    if 'original' in backup_filename.lower():
        new_name = new_name.replace('.py', '_original.py')
    elif 'backup' in backup_filename.lower():
        new_name = new_name.replace('.py', '_alternative.py')
    else:
        new_name = new_name.replace('.py', '_enhanced.py')
    
    return new_name

def safe_rename_backup_files():
    """Безопасное переименование backup файлов"""
    print("🔄 БЕЗОПАСНОЕ ПЕРЕИМЕНОВАНИЕ BACKUP ФАЙЛОВ")
    print("=" * 60)
    
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
    
    print(f"📊 НАЙДЕНО BACKUP ФАЙЛОВ: {len(backup_files)}")
    
    rename_plan = []
    risks = []
    
    # Анализируем каждый файл
    for i, backup_file in enumerate(backup_files, 1):
        print(f"\n📁 [{i}/{len(backup_files)}] Анализ: {backup_file.name}")
        
        # Генерируем новое имя
        new_name = generate_new_name(backup_file.name)
        new_path = backup_file.parent / new_name
        
        print(f"  🔄 Новое имя: {new_name}")
        
        # Анализируем зависимости
        dependencies = analyze_dependencies(backup_file)
        if 'error' in dependencies:
            print(f"  ❌ Ошибка анализа: {dependencies['error']}")
            continue
        
        # Ищем ссылки на файл
        references = find_references_to_file(backup_file.name, base_dir / 'security')
        
        # Оцениваем риски
        risk_level = "LOW"
        if len(references) > 0:
            risk_level = "MEDIUM"
        if len(dependencies['imports']) > 10:
            risk_level = "HIGH"
        
        print(f"  📊 Зависимости: {len(dependencies['imports'])} импортов")
        print(f"  🔍 Ссылки: {len(references)} файлов")
        print(f"  ⚠️ Риск: {risk_level}")
        
        # Сохраняем план
        rename_plan.append({
            'old_name': backup_file.name,
            'new_name': new_name,
            'old_path': str(backup_file),
            'new_path': str(new_path),
            'dependencies': dependencies,
            'references': references,
            'risk_level': risk_level
        })
        
        if risk_level == "HIGH":
            risks.append(backup_file.name)
    
    # Выводим план переименования
    print(f"\n📋 ПЛАН ПЕРЕИМЕНОВАНИЯ:")
    print("=" * 60)
    
    for item in rename_plan:
        print(f"📁 {item['old_name']}")
        print(f"   ➡️ {item['new_name']}")
        print(f"   ⚠️ Риск: {item['risk_level']}")
        print()
    
    # Предупреждения о рисках
    if risks:
        print(f"⚠️ ВЫСОКИЙ РИСК ({len(risks)} файлов):")
        for risk_file in risks:
            print(f"   • {risk_file}")
        print()
    
    # Создаем скрипт для переименования
    script_content = f"""#!/usr/bin/env python3
\"\"\"
Скрипт переименования backup файлов
Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
\"\"\"

import os
import shutil
from pathlib import Path

def rename_files():
    \"\"\"Переименование файлов\"\"\"
    backup_dir = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files')
    
    # Создаем резервную копию
    backup_backup_dir = backup_dir.parent / f"backup_files_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if backup_backup_dir.exists():
        shutil.rmtree(backup_backup_dir)
    shutil.copytree(backup_dir, backup_backup_dir)
    print(f"✅ Создана резервная копия: {{backup_backup_dir}}")
    
    # Переименовываем файлы
    rename_operations = {json.dumps([{'old': item['old_name'], 'new': item['new_name']} for item in rename_plan], indent=4)}
    
    for op in rename_operations:
        old_path = backup_dir / op['old']
        new_path = backup_dir / op['new']
        
        if old_path.exists():
            old_path.rename(new_path)
            print(f"✅ {{op['old']}} ➡️ {{op['new']}}")
        else:
            print(f"❌ Файл не найден: {{op['old']}}")
    
    print(f"\\n🎉 ПЕРЕИМЕНОВАНИЕ ЗАВЕРШЕНО!")
    print(f"📊 Переименовано файлов: {{len(rename_operations)}}")

if __name__ == "__main__":
    from datetime import datetime
    rename_files()
"""
    
    script_path = backup_dir / "rename_backup_files.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Сохраняем детальный план
    plan_path = backup_dir / f"RENAME_PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(rename_plan, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"📋 ПЛАН ПЕРЕИМЕНОВАНИЯ СОХРАНЕН: {plan_path}")
    print(f"🔧 СКРИПТ ПЕРЕИМЕНОВАНИЯ: {script_path}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print(f"1. 🔍 Проверьте план переименования")
    print(f"2. 🧪 Запустите скрипт: python3 {script_path}")
    print(f"3. ✅ Проверьте работу системы после переименования")
    print(f"4. 🔄 При проблемах восстановите из резервной копии")
    
    return rename_plan

if __name__ == "__main__":
    safe_rename_backup_files()