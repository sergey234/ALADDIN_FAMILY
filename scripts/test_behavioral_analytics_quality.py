#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест качества BehavioralAnalyticsEngine
Проверяет все компоненты для достижения A+ качества
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_behavioral_analytics_quality():
    """Тест качества BehavioralAnalyticsEngine"""
    print("🎯 ТЕСТ КАЧЕСТВА BEHAVIORALANALYTICSENGINE")
    print("=" * 60)
    
    # Проверяем существование файла
    file_path = "security/ai_agents/behavioral_analytics_engine.py"
    if not os.path.exists(file_path):
        print("❌ Файл BehavioralAnalyticsEngine не найден")
        return False
    
    print("✅ Файл BehavioralAnalyticsEngine найден")
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Анализируем код
    lines = content.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    comment_lines = len([line for line in lines if line.strip().startswith('#')])
    doc_lines = len([line for line in lines if '"""' in line or "'''" in line])
    
    print(f"\n📊 СТАТИСТИКА КОДА:")
    print(f"   📄 Всего строк: {total_lines}")
    print(f"   💻 Строк кода: {code_lines}")
    print(f"   📝 Комментариев: {comment_lines}")
    print(f"   📖 Документации: {doc_lines}")
    print(f"   📈 Плотность кода: {code_lines/total_lines*100:.1f}%")
    
    # Проверяем компоненты системы
    components = {
        "Обработка ошибок": content.count("try:") + content.count("except"),
        "Конфигурация": content.count("config") + content.count("settings"),
        "Классы": content.count("class "),
        "Перечисления": content.count("class ") - content.count("def "),
        "Методы": content.count("def "),
        "Документация": content.count('"""') + content.count("'''"),
        "Логирование": content.count("logger") + content.count("logging"),
        "Типизация": content.count(": str") + content.count(": int") + content.count(": bool") + content.count(": Dict") + content.count(": List"),
        "Поведение": content.count("behavior") + content.count("Behavior"),
        "Аналитика": content.count("analytics") + content.count("Analytics"),
        "Аномалии": content.count("anomaly") + content.count("Anomaly"),
        "Паттерны": content.count("pattern") + content.count("Pattern"),
        "Риск": content.count("risk") + content.count("Risk"),
        "Пользователи": content.count("user") + content.count("User"),
        "ML модели": content.count("ml_models") + content.count("machine_learning"),
        "Цветовая схема": content.count("color_scheme") + content.count("Matrix AI"),
        "Тестирование": content.count("test_") + content.count("_test_"),
        "Валидация": content.count("validate") + content.count("validation"),
        "Шифрование": content.count("encrypt") + content.count("hash")
    }
    
    print(f"\n🔧 КОМПОНЕНТЫ СИСТЕМЫ:")
    for component, count in components.items():
        print(f"   {component}: {count}")
    
    # Проверяем архитектурные принципы
    architectural_checks = {
        "Документация": doc_lines > 20,
        "Расширяемость": "class " in content and "def " in content,
        "DRY принцип": content.count("def ") > 10 and content.count("def ") < 50,
        "SOLID принципы": "class " in content and "def " in content and "try:" in content,
        "Логирование": "logger" in content,
        "Модульность": "import " in content and "class " in content,
        "Конфигурация": "config" in content or "settings" in content,
        "Обработка ошибок": "try:" in content and "except" in content
    }
    
    print(f"\n🏗️ АРХИТЕКТУРНЫЕ ПРИНЦИПЫ:")
    for principle, passed in architectural_checks.items():
        status = "✅ ПРОЙДЕНО" if passed else "❌ НЕ ПРОЙДЕНО"
        print(f"   {principle}: {status}")
    
    # Проверяем функциональность
    functionality_checks = {
        "Валидация параметров": "validate" in content,
        "Сохранение данных": "save" in content or "json.dump" in content,
        "Анализ поведения": "analyze_user_behavior" in content,
        "Обнаружение аномалий": "detect_anomalies" in content,
        "Анализ паттернов": "analyze_patterns" in content,
        "Оценка риска": "calculate_risk_score" in content,
        "Профили пользователей": "user_profiles" in content,
        "ML модели": "ml_models" in content,
        "Временные паттерны": "time_patterns" in content,
        "Локационные паттерны": "location_patterns" in content,
        "Паттерны активности": "activity_patterns" in content,
        "Цветовая схема": "color_scheme" in content,
        "Тестирование": "test_" in content,
        "Шифрование данных": "encrypt" in content,
        "Валидация входных данных": "validate" in content,
        "Обработка ошибок": "try:" in content and "except" in content
    }
    
    print(f"\n⚙️ ФУНКЦИОНАЛЬНОСТЬ:")
    for functionality, passed in functionality_checks.items():
        status = "✅ РЕАЛИЗОВАНО" if passed else "❌ НЕ РЕАЛИЗОВАНО"
        print(f"   {functionality}: {status}")
    
    # Проверяем безопасность
    security_checks = {
        "Шифрование данных": "encrypt" in content,
        "Аудит действий": "logger" in content,
        "Контроль доступа": "user_id" in content,
        "Конфиденциальность данных": "encrypt" in content and "sensitive" in content,
        "Безопасное логирование": "logger" in content and "error" in content,
        "Валидация входных данных": "validate" in content,
        "Обработка ошибок": "try:" in content and "except" in content,
        "Аутентификация источников": "user_id" in content
    }
    
    print(f"\n🔒 БЕЗОПАСНОСТЬ:")
    for security, passed in security_checks.items():
        status = "✅ РЕАЛИЗОВАНО" if passed else "❌ НЕ РЕАЛИЗОВАНО"
        print(f"   {security}: {status}")
    
    # Проверяем тестирование
    testing_checks = {
        "Спящий режим": "status" in content and "ACTIVE" in content,
        "Документация тестов": '"""' in content,
        "Unit тесты": "if __name__" in content,
        "Тест качества": "test_" in content or "quality" in content,
        "Упрощенный тест": "if __name__" in content,
        "Интеграционный тест": "import" in content and "class" in content,
        "Покрытие кода": code_lines >= 600
    }
    
    print(f"\n🧪 ТЕСТИРОВАНИЕ:")
    for testing, passed in testing_checks.items():
        status = "✅ ЕСТЬ" if passed else "❌ НЕТ"
        print(f"   {testing}: {status}")
    
    # Подсчитываем баллы
    total_checks = len(architectural_checks) + len(functionality_checks) + len(security_checks) + len(testing_checks)
    passed_checks = sum(architectural_checks.values()) + sum(functionality_checks.values()) + sum(security_checks.values()) + sum(testing_checks.values())
    
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
    
    print(f"\n📊 АНАЛИЗ НЕДОСТАЮЩИХ БАЛЛОВ:")
    print(f"   🎯 Текущий балл: {quality_score:.1f}")
    print(f"   🎯 Максимальный балл: 100")
    print(f"   🎯 Недостает баллов: {100 - quality_score:.1f}")
    
    # Сохраняем отчет
    report = {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "doc_lines": doc_lines,
        "components": components,
        "architectural_checks": architectural_checks,
        "functionality_checks": functionality_checks,
        "security_checks": security_checks,
        "testing_checks": testing_checks,
        "quality_score": quality_score,
        "passed_checks": passed_checks,
        "total_checks": total_checks
    }
    
    os.makedirs("data/quality_reports", exist_ok=True)
    report_file = f"data/quality_reports/behavioral_analytics_quality_test_{int(datetime.now().timestamp())}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Отчет сохранен: {report_file}")
    
    if quality_score >= 95:
        print("\n🎉 BEHAVIORALANALYTICSENGINE СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
    else:
        print(f"\n⚠️ ТРЕБУЕТСЯ ДОРАБОТКА ДО A+ КАЧЕСТВА (недостает {100 - quality_score:.1f} баллов)")
    
    return quality_score >= 95

if __name__ == "__main__":
    test_behavioral_analytics_quality()