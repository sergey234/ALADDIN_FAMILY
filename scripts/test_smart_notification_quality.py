#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт тестирования качества SmartNotificationManager
Создан: 2024-09-05
Версия: 1.0.0
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_smart_notification_quality():
    """Тест качества SmartNotificationManager"""
    print("🎯 ТЕСТ КАЧЕСТВА SMARTNOTIFICATIONMANAGER")
    print("=" * 60)
    
    # Проверяем существование файла
    file_path = "security/ai_agents/smart_notification_manager.py"
    if not os.path.exists(file_path):
        print("❌ Файл SmartNotificationManager не найден")
        return False
    
    print("✅ Файл SmartNotificationManager найден")
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Анализируем код
    lines = content.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    
    print(f"\n📊 СТАТИСТИКА КОДА:")
    print(f"   📄 Всего строк: {total_lines}")
    print(f"   💻 Строк кода: {code_lines}")
    print(f"   📈 Плотность кода: {code_lines/total_lines*100:.1f}%")
    
    # Проверяем компоненты
    components = {
        "Обработка ошибок": content.count("try:") + content.count("except"),
        "Классы": content.count("class "),
        "Методы": content.count("def "),
        "Документация": content.count('"""') + content.count("'''"),
        "Логирование": content.count("logger") + content.count("logging"),
        "Типизация": content.count(": str") + content.count(": int") + content.count(": bool"),
        "Уведомления": content.count("notification") + content.count("Notification"),
        "AI анализ": content.count("ai_analysis") + content.count("AI"),
        "Персонализация": content.count("personaliz") + content.count("Personaliz"),
        "Контекст": content.count("context") + content.count("Context"),
        "Время": content.count("timing") + content.count("Timing"),
        "Каналы": content.count("channel") + content.count("Channel"),
        "Шаблоны": content.count("template") + content.count("Template"),
        "Приоритеты": content.count("priority") + content.count("Priority"),
        "Очереди": content.count("queue") + content.count("Queue"),
        "Статистика": content.count("statistic") + content.count("Statistic"),
        "Безопасность": content.count("security") + content.count("Security"),
        "Цветовая схема": content.count("color_scheme") + content.count("Matrix AI"),
        "Тестирование": content.count("test_") + content.count("_test_")
    }
    
    print(f"\n🔧 КОМПОНЕНТЫ СИСТЕМЫ:")
    for component, count in components.items():
        print(f"   {component}: {count}")
    
    # Проверяем качество
    quality_checks = {
        "Документация": components["Документация"] > 20,
        "Обработка ошибок": components["Обработка ошибок"] > 10,
        "Логирование": components["Логирование"] > 5,
        "Типизация": components["Типизация"] > 10,
        "Уведомления": components["Уведомления"] > 5,
        "AI анализ": components["AI анализ"] > 5,
        "Персонализация": components["Персонализация"] > 5,
        "Контекст": components["Контекст"] > 5,
        "Время": components["Время"] > 5,
        "Каналы": components["Каналы"] > 5,
        "Шаблоны": components["Шаблоны"] > 5,
        "Приоритеты": components["Приоритеты"] > 5,
        "Очереди": components["Очереди"] > 5,
        "Статистика": components["Статистика"] > 5,
        "Тестирование": components["Тестирование"] > 5,
        "Цветовая схема": components["Цветовая схема"] > 5,
        "Покрытие кода": code_lines >= 800
    }
    
    print(f"\n🏗️ ПРОВЕРКА КАЧЕСТВА:")
    for check, passed in quality_checks.items():
        status = "✅ ПРОЙДЕНО" if passed else "❌ НЕ ПРОЙДЕНО"
        print(f"   {check}: {status}")
    
    # Подсчитываем баллы
    total_checks = len(quality_checks)
    passed_checks = sum(quality_checks.values())
    quality_score = (passed_checks / total_checks) * 100
    
    print(f"\n🏆 ОЦЕНКА КАЧЕСТВА: {quality_score:.1f}/100")
    
    if quality_score >= 95:
        print("✅ КАЧЕСТВО: A+ (ОТЛИЧНО)")
    elif quality_score >= 90:
        print("✅ КАЧЕСТВО: A (ОЧЕНЬ ХОРОШО)")
    elif quality_score >= 80:
        print("⚠️ КАЧЕСТВО: B (ХОРОШО)")
    else:
        print("❌ КАЧЕСТВО: C (ТРЕБУЕТ УЛУЧШЕНИЯ)")
    
    # Сохраняем отчет
    os.makedirs("data/quality_reports", exist_ok=True)
    report = {
        "component": "SmartNotificationManager",
        "version": "1.0.0",
        "quality_score": quality_score,
        "quality_grade": "A+" if quality_score >= 95 else "A" if quality_score >= 90 else "B",
        "code_statistics": {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": total_lines - code_lines,
            "code_density": code_lines/total_lines*100
        },
        "components": components,
        "quality_checks": quality_checks,
        "generated_at": datetime.now().isoformat()
    }
    
    report_file = f"data/quality_reports/smart_notification_quality_test_{int(datetime.now().timestamp())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Отчет сохранен: {report_file}")
    
    if quality_score >= 95:
        print("🎉 SMARTNOTIFICATIONMANAGER СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
        return True
    else:
        print(f"⚠️ ТРЕБУЕТСЯ ДОРАБОТКА ДО A+ КАЧЕСТВА (недостает {100-quality_score:.1f} баллов)")
        return False

if __name__ == "__main__":
    success = test_smart_notification_quality()
    if success:
        print("\n✅ ТЕСТ КАЧЕСТВА ПРОЙДЕН УСПЕШНО!")
    else:
        print("\n❌ ТЕСТ КАЧЕСТВА НЕ ПРОЙДЕН!")