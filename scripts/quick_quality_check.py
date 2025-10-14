#!/usr/bin/env python3
"""
БЫСТРАЯ ПРОВЕРКА КАЧЕСТВА КОДА
Простой и надежный скрипт для проверки качества
"""

import os
import re
from typing import Dict, Any

def quick_quality_check(filename: str) -> Dict[str, Any]:
    """
    Быстрая проверка качества кода
    
    Args:
        filename: Путь к файлу
        
    Returns:
        Dict с метриками качества
    """
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
        complexity = 0
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'try:', 'except:', 'with ', 'def ', 'class ']):
                complexity += 1
        
        # Расчет процентов
        doc_percent = (doc_lines / total_lines) * 100
        type_hints_percent = (type_hint_lines / total_lines) * 100
        complexity_percent = (complexity / total_lines) * 100
        
        # Итоговый балл
        final_score = (doc_percent * 0.3 + type_hints_percent * 0.2 + complexity_percent * 0.3 + 100 * 0.2)
        
        # Определение качества
        if final_score >= 95:
            quality = "A+"
        elif final_score >= 90:
            quality = "A"
        elif final_score >= 85:
            quality = "B+"
        elif final_score >= 80:
            quality = "B"
        elif final_score >= 70:
            quality = "C"
        else:
            quality = "D"
        
        return {
            'filename': os.path.basename(filename),
            'total_lines': total_lines,
            'doc_percent': round(doc_percent, 1),
            'type_hints_percent': round(type_hints_percent, 1),
            'complexity_percent': round(complexity_percent, 1),
            'final_score': round(final_score, 1),
            'quality': quality
        }
        
    except Exception as e:
        print(f"Ошибка анализа файла {filename}: {e}")
        return {}

def main():
    """Основная функция"""
    print("🔍 БЫСТРАЯ ПРОВЕРКА КАЧЕСТВА КОДА")
    print("=" * 50)
    
    files_to_check = [
        'security/ai_agents/family_communication_hub.py',
        'security/ai_agents/emergency_response_interface.py',
        'security/ai_agents/notification_bot.py',
        'security/ai_agents/family_communication_hub_a_plus.py'
    ]
    
    results = []
    total_score = 0
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\n📋 {os.path.basename(filename)}:")
            print("-" * 30)
            
            result = quick_quality_check(filename)
            if result:
                results.append(result)
                total_score += result['final_score']
                
                print(f"  📊 Строки: {result['total_lines']}")
                print(f"  📖 Документация: {result['doc_percent']}%")
                print(f"  🏷️  Type hints: {result['type_hints_percent']}%")
                print(f"  🧠 Сложность: {result['complexity_percent']}%")
                print(f"  🎯 Балл: {result['final_score']}%")
                print(f"  🏆 Качество: {result['quality']}")
    
    # Итоговая статистика
    if results:
        avg_score = total_score / len(results)
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print("=" * 50)
        print(f"🎯 Средний балл: {avg_score:.1f}%")
        print(f"🔢 Компонентов: {len(results)}")
        
        if avg_score >= 95:
            print(f"🏆 ОБЩЕЕ КАЧЕСТВО: A+")
        elif avg_score >= 90:
            print(f"🥇 ОБЩЕЕ КАЧЕСТВО: A")
        elif avg_score >= 85:
            print(f"🥈 ОБЩЕЕ КАЧЕСТВО: B+")
        elif avg_score >= 80:
            print(f"🥉 ОБЩЕЕ КАЧЕСТВО: B")
        else:
            print(f"⚠️ ОБЩЕЕ КАЧЕСТВО: C")
        
        print(f"\n🎉 ПРОВЕРКА ЗАВЕРШЕНА!")

if __name__ == "__main__":
    main()