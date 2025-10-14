#!/usr/bin/env python3
"""
ПРОСТОЙ СКРИПТ ПРОВЕРКИ КАЧЕСТВА
Быстрый и надежный анализ кода
"""

import os
import re

def check_file_quality(filename):
    """Простая проверка качества файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        total_lines = len(lines)
        
        # Подсчет документации
        doc_lines = 0
        for line in lines:
            line = line.strip()
            if line.startswith('#') or '"""' in line or "'''" in line:
                doc_lines += 1
        
        # Подсчет type hints
        type_hint_lines = 0
        for line in lines:
            if any(keyword in line for keyword in ['->', ': int', ': str', ': float', ': bool', ': List', ': Dict', ': Tuple', ': Optional', ': Union', ': Any', ': Callable']):
                type_hint_lines += 1
        
        # Подсчет сложности (простой)
        complexity_lines = 0
        for line in lines:
            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'try:', 'except', 'with ', 'def ', 'class ']):
                complexity_lines += 1
        
        # Расчет процентов
        doc_percent = (doc_lines / total_lines) * 100
        type_hints_percent = (type_hint_lines / total_lines) * 100
        complexity_percent = (complexity_lines / total_lines) * 100
        
        # Итоговый балл
        final_score = (doc_percent * 0.3 + type_hints_percent * 0.2 + complexity_percent * 0.3 + 100 * 0.2)
        
        return {
            'filename': os.path.basename(filename),
            'total_lines': total_lines,
            'doc_percent': round(doc_percent, 1),
            'type_hints_percent': round(type_hints_percent, 1),
            'complexity_percent': round(complexity_percent, 1),
            'final_score': round(final_score, 1),
            'quality': 'A+' if final_score >= 95 else 'A' if final_score >= 90 else 'B+' if final_score >= 85 else 'B' if final_score >= 80 else 'C'
        }
        
    except Exception as e:
        print(f"Ошибка анализа {filename}: {e}")
        return None

def main():
    """Основная функция"""
    print("🔍 ПРОСТАЯ ПРОВЕРКА КАЧЕСТВА КОДА")
    print("=" * 50)
    
    files = [
        'security/ai_agents/family_communication_hub_a_plus.py',
        'security/ai_agents/family_communication_hub.py',
        'security/ai_agents/emergency_response_interface.py',
        'security/ai_agents/notification_bot.py'
    ]
    
    for filename in files:
        if os.path.exists(filename):
            print(f"\n📋 {os.path.basename(filename)}:")
            print("-" * 30)
            
            result = check_file_quality(filename)
            if result:
                print(f"  📊 Строки: {result['total_lines']}")
                print(f"  📖 Документация: {result['doc_percent']}%")
                print(f"  🏷️  Type hints: {result['type_hints_percent']}%")
                print(f"  🧠 Сложность: {result['complexity_percent']}%")
                print(f"  🎯 ИТОГОВЫЙ БАЛЛ: {result['final_score']}%")
                print(f"  🏆 КАЧЕСТВО: {result['quality']}")

if __name__ == "__main__":
    main()