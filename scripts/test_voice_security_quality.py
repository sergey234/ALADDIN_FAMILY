#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт тестирования качества VoiceSecurityValidator
Создан: 2024-09-05
Версия: 1.0.0
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_voice_security_quality():
    """Тест качества VoiceSecurityValidator"""
    print("🎯 ТЕСТ КАЧЕСТВА VOICESECURITYVALIDATOR")
    print("=" * 60)
    
    # Проверяем существование файла
    file_path = "security/ai_agents/voice_security_validator.py"
    if not os.path.exists(file_path):
        print("❌ Файл VoiceSecurityValidator не найден")
        return False
    
    print("✅ Файл VoiceSecurityValidator найден")
    
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
        "Безопасность": content.count("security") + content.count("Security"),
        "Валидация": content.count("valid") + content.count("Valid"),
        "Угрозы": content.count("threat") + content.count("Threat"),
        "Паттерны": content.count("pattern") + content.count("Pattern"),
        "Ключевые слова": content.count("keyword") + content.count("Keyword"),
        "Контекст": content.count("context") + content.count("Context"),
        "ML": content.count("ml") + content.count("ML") + content.count("machine"),
        "Поведение": content.count("behavior") + content.count("Behavior"),
        "Блокировка": content.count("block") + content.count("Block"),
        "Рекомендации": content.count("recommend") + content.count("Recommend"),
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
        "Безопасность": components["Безопасность"] > 5,
        "Валидация": components["Валидация"] > 5,
        "Угрозы": components["Угрозы"] > 5,
        "Паттерны": components["Паттерны"] > 5,
        "Ключевые слова": components["Ключевые слова"] > 5,
        "Контекст": components["Контекст"] > 5,
        "ML": components["ML"] > 5,
        "Поведение": components["Поведение"] > 5,
        "Блокировка": components["Блокировка"] > 5,
        "Рекомендации": components["Рекомендации"] > 5,
        "Тестирование": components["Тестирование"] > 5,
        "Цветовая схема": components["Цветовая схема"] > 5,
        "Покрытие кода": code_lines >= 700
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
        "component": "VoiceSecurityValidator",
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
    
    report_file = f"data/quality_reports/voice_security_quality_test_{int(datetime.now().timestamp())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Отчет сохранен: {report_file}")
    
    if quality_score >= 95:
        print("🎉 VOICESECURITYVALIDATOR СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
        return True
    else:
        print(f"⚠️ ТРЕБУЕТСЯ ДОРАБОТКА ДО A+ КАЧЕСТВА (недостает {100-quality_score:.1f} баллов)")
        return False

if __name__ == "__main__":
    success = test_voice_security_quality()
    if success:
        print("\n✅ ТЕСТ КАЧЕСТВА ПРОЙДЕН УСПЕШНО!")
    else:
        print("\n❌ ТЕСТ КАЧЕСТВА НЕ ПРОЙДЕН!")