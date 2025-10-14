#!/usr/bin/env python3
"""
Точный анализ ошибок flake8
"""

import re
import json
from collections import Counter
import matplotlib.pyplot as plt

def analyze_flake8_file(filename):
    """Анализ файла с ошибками flake8"""
    error_counts = Counter()
    total_errors = 0
    files_with_errors = set()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Ищем паттерн: file.py:line:col: E123 error message
                match = re.match(r'^([^:]+):(\d+):(\d+):\s+([EWF]\d+)\s+(.*)$', line)
                if match:
                    file_path = match.group(1)
                    error_code = match.group(4)
                    error_counts[error_code] += 1
                    total_errors += 1
                    files_with_errors.add(file_path)
                else:
                    # Попробуем другой паттерн
                    if ':' in line and any(code in line for code in ['E501', 'W293', 'E302', 'F401']):
                        parts = line.split(':')
                        if len(parts) >= 4:
                            file_path = parts[0]
                            error_part = parts[2].strip()
                            if error_part and any(code in error_part for code in ['E', 'W', 'F']):
                                error_code = error_part.split()[0]
                                if re.match(r'^[EWF]\d+$', error_code):
                                    error_counts[error_code] += 1
                                    total_errors += 1
                                    files_with_errors.add(file_path)
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
    
    return error_counts, total_errors, len(files_with_errors)

def create_error_chart(error_counts, title, filename):
    """Создание графика ошибок"""
    if not error_counts:
        print(f"Нет данных для {title}")
        return
    
    # Сортируем ошибки по количеству
    sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Берем топ-15 ошибок
    top_errors = sorted_errors[:15]
    error_codes = [item[0] for item in top_errors]
    error_counts_list = [item[1] for item in top_errors]
    
    # Создаем график
    plt.figure(figsize=(12, 8))
    bars = plt.bar(range(len(error_codes)), error_counts_list, color='skyblue', edgecolor='navy', alpha=0.7)
    
    # Настраиваем график
    plt.title(f'{title}\nВсего ошибок: {sum(error_counts_list)}', fontsize=14, fontweight='bold')
    plt.xlabel('Коды ошибок flake8', fontsize=12)
    plt.ylabel('Количество ошибок', fontsize=12)
    plt.xticks(range(len(error_codes)), error_codes, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Добавляем значения на столбцы
    for i, (bar, count) in enumerate(zip(bars, error_counts_list)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(count), ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"График сохранен: {filename}")

def create_comparison_chart(data, filename):
    """Создание сравнительного графика"""
    categories = list(data.keys())
    error_types = ['E501', 'W293', 'E302', 'F401', 'E128', 'F811', 'E402', 'W291', 'E302', 'E305']
    
    # Создаем данные для группированного графика
    chart_data = {}
    for category in categories:
        chart_data[category] = [data[category].get(error_type, 0) for error_type in error_types]
    
    # Создаем график
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = range(len(error_types))
    width = 0.25
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    for i, (category, values) in enumerate(chart_data.items()):
        ax.bar([pos + width * i for pos in x], values, width, 
               label=category, color=colors[i % len(colors)], alpha=0.8)
    
    ax.set_xlabel('Типы ошибок flake8', fontsize=12)
    ax.set_ylabel('Количество ошибок', fontsize=12)
    ax.set_title('Сравнение ошибок flake8 по категориям', fontsize=14, fontweight='bold')
    ax.set_xticks([pos + width for pos in x])
    ax.set_xticklabels(error_types, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Сравнительный график сохранен: {filename}")

def main():
    """Основная функция"""
    print("🔍 ТОЧНЫЙ АНАЛИЗ ОШИБОК FLAKE8")
    print("=" * 50)
    
    # Анализируем три файла
    files_to_analyze = [
        ("flake8_all_474_files.txt", "Все 474 файла системы"),
        ("flake8_security_242_files.txt", "242 файла системы безопасности"),
        ("flake8_sfm_only.txt", "Safe Function Manager")
    ]
    
    all_data = {}
    
    for filename, title in files_to_analyze:
        print(f"\n📊 Анализ: {title}")
        print("-" * 30)
        
        error_counts, total_errors, files_with_errors = analyze_flake8_file(filename)
        all_data[title] = error_counts
        
        print(f"Всего ошибок: {total_errors}")
        print(f"Файлов с ошибками: {files_with_errors}")
        print(f"Топ-10 ошибок:")
        
        for error_code, count in list(error_counts.most_common(10)):
            print(f"  {error_code}: {count}")
        
        # Создаем индивидуальный график
        chart_filename = f"flake8_chart_{filename.replace('.txt', '')}.png"
        create_error_chart(error_counts, title, chart_filename)
    
    # Создаем сравнительный график
    print(f"\n📈 Создание сравнительного графика...")
    create_comparison_chart(all_data, "flake8_comparison_chart.png")
    
    # Сохраняем детальный отчет
    report = {
        "analysis_timestamp": "2025-09-13T22:55:00",
        "categories": {}
    }
    
    for filename, title in files_to_analyze:
        error_counts, total_errors, files_with_errors = analyze_flake8_file(filename)
        report["categories"][title] = {
            "total_errors": total_errors,
            "files_with_errors": files_with_errors,
            "error_breakdown": dict(error_counts)
        }
    
    with open("flake8_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Детальный отчет сохранен: flake8_analysis_report.json")
    print("\n✅ Анализ завершен!")

if __name__ == "__main__":
    main()