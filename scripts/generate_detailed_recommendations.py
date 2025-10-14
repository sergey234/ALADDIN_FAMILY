#!/usr/bin/env python3
"""
Генератор детальных рекомендаций по backup файлам
"""

import json
from pathlib import Path
from datetime import datetime

def load_analysis_report():
    """Загрузка отчета анализа"""
    report_dir = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files')
    report_files = list(report_dir.glob('FUNCTIONALITY_ANALYSIS_REPORT_*.json'))
    
    if not report_files:
        print("❌ Отчет анализа не найден!")
        return None
    
    # Берем самый новый отчет
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_report, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_detailed_recommendations(analysis_data):
    """Генерация детальных рекомендаций"""
    
    print("🎯 ДЕТАЛЬНЫЕ РЕКОМЕНДАЦИИ ПО BACKUP ФАЙЛАМ")
    print("=" * 80)
    
    # Категоризируем файлы по типу рекомендаций
    categories = {
        'keep_both': [],
        'check_carefully': [],
        'can_remove': [],
        'critical_differences': []
    }
    
    for item in analysis_data:
        comparison = item['comparison']
        diff_ratio = comparison.get('diff_ratio', 0)
        
        if diff_ratio > 100:
            categories['critical_differences'].append(item)
        elif diff_ratio > 50:
            categories['keep_both'].append(item)
        elif diff_ratio > 20:
            categories['check_carefully'].append(item)
        else:
            categories['can_remove'].append(item)
    
    # Выводим рекомендации по категориям
    print(f"\n🚨 КРИТИЧЕСКИЕ РАЗЛИЧИЯ ({len(categories['critical_differences'])} файлов):")
    print("   НЕ УДАЛЯТЬ - файлы кардинально разные!")
    for item in categories['critical_differences']:
        print(f"   • {item['backup_name']} vs {item['original_name']}")
        print(f"     Различия: {item['comparison']['diff_ratio']:.1f}%")
        print(f"     Размер: backup {item['comparison']['size_comparison']['backup_size']:,} vs original {item['comparison']['size_comparison']['original_size']:,}")
        print()
    
    print(f"\n🔄 СОХРАНИТЬ ОБА ({len(categories['keep_both'])} файлов):")
    print("   Файлы имеют значительные различия в функциональности")
    for item in categories['keep_both']:
        print(f"   • {item['backup_name']} vs {item['original_name']}")
        print(f"     Различия: {item['comparison']['diff_ratio']:.1f}%")
        print()
    
    print(f"\n⚠️ ПРОВЕРИТЬ ДЕТАЛЬНО ({len(categories['check_carefully'])} файлов):")
    print("   Файлы имеют небольшие различия - нужна детальная проверка")
    for item in categories['check_carefully']:
        print(f"   • {item['backup_name']} vs {item['original_name']}")
        print(f"     Различия: {item['comparison']['diff_ratio']:.1f}%")
        print()
    
    print(f"\n✅ МОЖНО УДАЛИТЬ ({len(categories['can_remove'])} файлов):")
    print("   Файлы практически идентичны")
    for item in categories['can_remove']:
        print(f"   • {item['backup_name']} vs {item['original_name']}")
        print(f"     Различия: {item['comparison']['diff_ratio']:.1f}%")
        print()
    
    # Детальный анализ каждого файла
    print("\n" + "="*80)
    print("📋 ДЕТАЛЬНЫЙ АНАЛИЗ КАЖДОГО ФАЙЛА")
    print("="*80)
    
    for i, item in enumerate(analysis_data, 1):
        print(f"\n📁 [{i}] {item['backup_name']}")
        print(f"   🔍 Оригинал: {item['original_name']}")
        
        comparison = item['comparison']
        class_comp = comparison['class_comparison']
        func_comp = comparison['function_comparison']
        import_comp = comparison['import_comparison']
        size_comp = comparison['size_comparison']
        
        print(f"   📊 Размер: backup {size_comp['backup_size']:,} vs original {size_comp['original_size']:,}")
        print(f"   📈 Различия: {comparison['diff_ratio']:.1f}%")
        
        # Классы
        if class_comp['backup_only']:
            print(f"   🏗️ Уникальные классы в backup: {', '.join(class_comp['backup_only'])}")
        if class_comp['original_only']:
            print(f"   🏗️ Уникальные классы в оригинале: {', '.join(class_comp['original_only'])}")
        
        # Функции
        if func_comp['backup_only']:
            print(f"   ⚡ Уникальные функции в backup: {len(func_comp['backup_only'])} шт.")
            if len(func_comp['backup_only']) <= 10:
                print(f"      {', '.join(func_comp['backup_only'])}")
        if func_comp['original_only']:
            print(f"   ⚡ Уникальные функции в оригинале: {len(func_comp['original_only'])} шт.")
            if len(func_comp['original_only']) <= 10:
                print(f"      {', '.join(func_comp['original_only'])}")
        
        # Импорты
        if import_comp['backup_only']:
            print(f"   📦 Дополнительные импорты в backup: {len(import_comp['backup_only'])} шт.")
        if import_comp['original_only']:
            print(f"   📦 Дополнительные импорты в оригинале: {len(import_comp['original_only'])} шт.")
        
        # Рекомендации
        print(f"   🎯 Рекомендация: {item['recommendations'][-1] if item['recommendations'] else 'Не определено'}")
    
    return categories

def main():
    """Основная функция"""
    print("🔍 ЗАГРУЗКА ОТЧЕТА АНАЛИЗА...")
    
    analysis_data = load_analysis_report()
    if not analysis_data:
        return
    
    print(f"✅ Загружено {len(analysis_data)} файлов для анализа")
    
    # Генерируем детальные рекомендации
    categories = generate_detailed_recommendations(analysis_data)
    
    # Сохраняем итоговый отчет
    report_file = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files/DETAILED_RECOMMENDATIONS.md')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# ДЕТАЛЬНЫЕ РЕКОМЕНДАЦИИ ПО BACKUP ФАЙЛАМ\n\n")
        f.write(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## СВОДКА ПО КАТЕГОРИЯМ\n\n")
        f.write(f"- 🚨 Критические различия: {len(categories['critical_differences'])} файлов\n")
        f.write(f"- 🔄 Сохранить оба: {len(categories['keep_both'])} файлов\n")
        f.write(f"- ⚠️ Проверить детально: {len(categories['check_carefully'])} файлов\n")
        f.write(f"- ✅ Можно удалить: {len(categories['can_remove'])} файлов\n\n")
        
        f.write("## РЕКОМЕНДАЦИИ\n\n")
        f.write("1. **НЕ УДАЛЯТЬ** файлы с критическими различиями (>100%)\n")
        f.write("2. **СОХРАНИТЬ ОБА** файла с значительными различиями (50-100%)\n")
        f.write("3. **ПРОВЕРИТЬ ДЕТАЛЬНО** файлы с небольшими различиями (20-50%)\n")
        f.write("4. **МОЖНО УДАЛИТЬ** файлы с минимальными различиями (<20%)\n\n")
        
        f.write("## ДЕТАЛЬНЫЙ АНАЛИЗ\n\n")
        for i, item in enumerate(analysis_data, 1):
            f.write(f"### {i}. {item['backup_name']}\n\n")
            f.write(f"- **Оригинал:** {item['original_name']}\n")
            f.write(f"- **Различия:** {item['comparison']['diff_ratio']:.1f}%\n")
            f.write(f"- **Размер:** backup {item['comparison']['size_comparison']['backup_size']:,} vs original {item['comparison']['size_comparison']['original_size']:,}\n")
            f.write(f"- **Рекомендация:** {item['recommendations'][-1] if item['recommendations'] else 'Не определено'}\n\n")
    
    print(f"\n📋 ДЕТАЛЬНЫЙ ОТЧЕТ СОХРАНЕН: {report_file}")
    print(f"📊 ПРОАНАЛИЗИРОВАНО: {len(analysis_data)} файлов")

if __name__ == "__main__":
    main()