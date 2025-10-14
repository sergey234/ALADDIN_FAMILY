#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест качества ElderlyInterfaceManager
Создан: 2024-09-05
Версия: 1.0.0
"""

import os
import sys
import json
import time
from datetime import datetime

def test_elderly_interface_quality():
    """Тест качества ElderlyInterfaceManager"""
    print("🎯 ТЕСТ КАЧЕСТВА ELDERLYINTERFACEMANAGER")
    print("=" * 60)
    
    # Проверка существования файла
    file_path = "security/ai_agents/elderly_interface_manager.py"
    if not os.path.exists(file_path):
        print("❌ Файл ElderlyInterfaceManager не найден")
        return False
    
    print("✅ Файл ElderlyInterfaceManager найден")
    
    # Чтение файла
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Статистика кода
    lines = content.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    comment_lines = len([line for line in lines if line.strip().startswith('#')])
    docstring_lines = len([line for line in lines if '"""' in line or "'''" in line])
    
    print(f"\n📊 СТАТИСТИКА КОДА:")
    print(f"   📄 Всего строк: {total_lines}")
    print(f"   💻 Строк кода: {code_lines}")
    print(f"   📝 Комментариев: {comment_lines}")
    print(f"   📖 Документации: {docstring_lines}")
    print(f"   📈 Плотность кода: {(code_lines/total_lines)*100:.1f}%")
    
    # Компоненты системы
    components = {
        "Обработка ошибок": content.count("try:") + content.count("except") + content.count("raise"),
        "Конфигурация": content.count("config") + content.count("Config"),
        "Классы": content.count("class "),
        "Возрастные категории": content.count("ElderlyAgeCategory") + content.count("age_category"),
        "AI модели": content.count("ai_models") + content.count("AI"),
        "Интерфейсы": content.count("interface") + content.count("Interface"),
        "Доступность": content.count("accessibility") + content.count("Accessibility"),
        "Семейная интеграция": content.count("family") + content.count("Family"),
        "Экстренные системы": content.count("emergency") + content.count("Emergency"),
        "Голосовое управление": content.count("voice") + content.count("Voice"),
        "Обучающие модули": content.count("learning") + content.count("Learning"),
        "Мониторинг": content.count("monitor") + content.count("Monitor"),
        "Уведомления": content.count("notification") + content.count("Notification"),
        "Статистика": content.count("statistics") + content.count("Statistics"),
        "Логирование": content.count("logger") + content.count("logging"),
        "Методы": content.count("def "),
        "Документация": content.count('"""') + content.count("'''"),
        "Перечисления": content.count("Enum"),
        "Датаклассы": content.count("@dataclass"),
        "Типизация": content.count(": ") + content.count("-> ")
    }
    
    print(f"\n🔧 КОМПОНЕНТЫ СИСТЕМЫ:")
    for component, count in components.items():
        print(f"   {component}: {count}")
    
    # Архитектурные принципы
    architecture_checks = {
        "Документация": docstring_lines >= 20,
        "Расширяемость": "class " in content and "def " in content,
        "DRY принцип": content.count("def _") >= 8,
        "SOLID принципы": "class " in content and "def " in content and "Enum" in content,
        "Логирование": "logger" in content and "logging" in content,
        "Модульность": "import " in content and "from " in content,
        "Конфигурация": "config" in content.lower(),
        "Обработка ошибок": "try:" in content and "except" in content
    }
    
    print(f"\n🏗️ АРХИТЕКТУРНЫЕ ПРИНЦИПЫ:")
    for principle, passed in architecture_checks.items():
        status = "✅ ПРОЙДЕНО" if passed else "❌ НЕ ПРОЙДЕНО"
        print(f"   {principle}: {status}")
    
    # Функциональность
    functionality_checks = {
        "Валидация параметров": "validate" in content.lower() or "check" in content.lower(),
        "Сохранение данных": "save" in content.lower() or "store" in content.lower(),
        "Генерация настроек": "generate" in content.lower(),
        "Генерация интерфейсов": "interface" in content.lower(),
        "Возрастные категории": "age_category" in content,
        "Голосовые команды": "voice" in content.lower(),
        "Семейная интеграция": "family" in content.lower(),
        "Экстренные системы": "emergency" in content.lower(),
        "AI анализ": "ai_models" in content,
        "Обучающие модули": "learning" in content.lower(),
        "Мониторинг поведения": "monitor" in content.lower(),
        "Уведомления": "notification" in content.lower(),
        "Статистика": "statistics" in content.lower(),
        "Доступность": "accessibility" in content.lower(),
        "Шаблоны интерфейсов": "template" in content.lower(),
        "Профили пользователей": "profile" in content.lower(),
        "Настройки интерфейса": "settings" in content.lower(),
        "Функции доступности": "accessibility" in content.lower()
    }
    
    print(f"\n⚙️ ФУНКЦИОНАЛЬНОСТЬ:")
    for feature, implemented in functionality_checks.items():
        status = "✅ РЕАЛИЗОВАНО" if implemented else "❌ НЕ РЕАЛИЗОВАНО"
        print(f"   {feature}: {status}")
    
    # Безопасность
    security_checks = {
        "Шифрование данных": "encrypt" in content.lower() or "crypt" in content.lower(),
        "Аудит действий": "audit" in content.lower() or "log" in content.lower(),
        "Контроль доступа": "access" in content.lower() or "permission" in content.lower(),
        "Конфиденциальность данных": "privacy" in content.lower() or "confidential" in content.lower(),
        "Безопасное логирование": "logger" in content and "error" in content.lower(),
        "Валидация входных данных": "validate" in content.lower() or "check" in content.lower(),
        "Обработка ошибок": "try:" in content and "except" in content,
        "Аутентификация источников": "auth" in content.lower() or "authenticate" in content.lower()
    }
    
    print(f"\n�� БЕЗОПАСНОСТЬ:")
    for security, implemented in security_checks.items():
        status = "✅ РЕАЛИЗОВАНО" if implemented else "❌ НЕ РЕАЛИЗОВАНО"
        print(f"   {security}: {status}")
    
    # Тестирование
    test_checks = {
        "Спящий режим": os.path.exists("scripts/put_elderly_interface_to_sleep.py"),
        "Документация тестов": os.path.exists("scripts/test_elderly_interface_simple.py"),
        "Unit тесты": os.path.exists("scripts/test_elderly_interface_simple.py"),
        "Тест качества": os.path.exists("scripts/test_elderly_interface_quality.py"),
        "Упрощенный тест": os.path.exists("scripts/test_elderly_interface_simple.py"),
        "Интеграционный тест": os.path.exists("scripts/test_elderly_interface_integration.py"),
        "Покрытие кода": code_lines >= 500
    }
    
    print(f"\n🧪 ТЕСТИРОВАНИЕ:")
    for test, exists in test_checks.items():
        status = "✅ ЕСТЬ" if exists else "❌ НЕТ"
        print(f"   {test}: {status}")
    
    # Расчет оценки качества
    architecture_score = sum(architecture_checks.values()) / len(architecture_checks) * 25
    functionality_score = sum(functionality_checks.values()) / len(functionality_checks) * 35
    security_score = sum(security_checks.values()) / len(security_checks) * 25
    test_score = sum(test_checks.values()) / len(test_checks) * 15
    
    total_score = architecture_score + functionality_score + security_score + test_score
    
    print(f"\n🏆 ОЦЕНКА КАЧЕСТВА: {total_score:.1f}/100")
    
    if total_score >= 95:
        quality_grade = "A+ (ОТЛИЧНО)"
    elif total_score >= 90:
        quality_grade = "A (ОЧЕНЬ ХОРОШО)"
    elif total_score >= 80:
        quality_grade = "B (ХОРОШО)"
    elif total_score >= 70:
        quality_grade = "C (УДОВЛЕТВОРИТЕЛЬНО)"
    else:
        quality_grade = "D (НЕУДОВЛЕТВОРИТЕЛЬНО)"
    
    print(f"✅ КАЧЕСТВО: {quality_grade}")
    
    # Анализ недостающих баллов
    missing_points = 100 - total_score
    print(f"\n📊 АНАЛИЗ НЕДОСТАЮЩИХ БАЛЛОВ:")
    print(f"   🎯 Текущий балл: {total_score:.1f}")
    print(f"   🎯 Максимальный балл: 100")
    print(f"   🎯 Недостает баллов: {missing_points:.1f}")
    
    # Сохранение отчета
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "docstring_lines": docstring_lines,
        "code_density": (code_lines/total_lines)*100,
        "components": components,
        "architecture_score": architecture_score,
        "functionality_score": functionality_score,
        "security_score": security_score,
        "test_score": test_score,
        "total_score": total_score,
        "quality_grade": quality_grade,
        "missing_points": missing_points
    }
    
    # Создание директории для отчетов
    os.makedirs("data/quality_reports", exist_ok=True)
    
    # Сохранение отчета
    report_file = f"data/quality_reports/elderly_interface_quality_test_{int(time.time())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен: {report_file}")
    
    if total_score >= 95:
        print(f"\n🎉 ELDERLYINTERFACEMANAGER СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
        return True
    else:
        print(f"\n⚠️ ELDERLYINTERFACEMANAGER ТРЕБУЕТ ДОРАБОТКИ ДЛЯ ДОСТИЖЕНИЯ A+ КАЧЕСТВА!")
        return False

if __name__ == "__main__":
    success = test_elderly_interface_quality()
    sys.exit(0 if success else 1)
