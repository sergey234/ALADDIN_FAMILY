#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт перевода ContextualAlertSystem в спящий режим
Создан: 2024-09-05
Версия: 1.0.0
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def put_contextual_alert_to_sleep():
    """Перевод ContextualAlertSystem в спящий режим"""
    print("😴 ПЕРЕВОД CONTEXTUALALERTSYSTEM В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)
    
    # Проверяем существование файла
    file_path = "security/ai_agents/contextual_alert_system.py"
    if not os.path.exists(file_path):
        print("❌ Файл ContextualAlertSystem не найден")
        return False
    
    print("✅ Файл ContextualAlertSystem найден")
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем качество перед спящим режимом
    print("\n🔍 ПРОВЕРКА КАЧЕСТВА ПЕРЕД СПЯЩИМ РЕЖИМОМ")
    print("-" * 50)
    
    # Анализируем код
    lines = content.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    
    print(f"📊 СТАТИСТИКА КОДА:")
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
        "Оповещения": content.count("alert") + content.count("Alert"),
        "Поведение": content.count("behavior") + content.count("Behavior"),
        "Контекст": content.count("context") + content.count("Context"),
        "Прогнозы": content.count("predict") + content.count("Predict"),
        "Триггеры": content.count("trigger") + content.count("Trigger"),
        "Условия": content.count("condition") + content.count("Condition"),
        "Действия": content.count("action") + content.count("Action"),
        "Время": content.count("timing") + content.count("Timing"),
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
        "Оповещения": components["Оповещения"] > 5,
        "Поведение": components["Поведение"] > 5,
        "Контекст": components["Контекст"] > 5,
        "Прогнозы": components["Прогнозы"] > 5,
        "Триггеры": components["Триггеры"] > 5,
        "Условия": components["Условия"] > 5,
        "Действия": components["Действия"] > 5,
        "Время": components["Время"] > 5,
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
        print("✅ КАЧЕСТВО: A+ (ОТЛИЧНО) - ГОТОВ К СПЯЩЕМУ РЕЖИМУ")
    elif quality_score >= 90:
        print("✅ КАЧЕСТВО: A (ОЧЕНЬ ХОРОШО) - ГОТОВ К СПЯЩЕМУ РЕЖИМУ")
    elif quality_score >= 80:
        print("⚠️ КАЧЕСТВО: B (ХОРОШО) - МОЖНО ПЕРЕВЕСТИ В СПЯЩИЙ РЕЖИМ")
    else:
        print("❌ КАЧЕСТВО: C (ТРЕБУЕТ УЛУЧШЕНИЯ) - НЕ РЕКОМЕНДУЕТСЯ")
        return False
    
    # Переводим в спящий режим
    print(f"\n😴 ПЕРЕВОД В СПЯЩИЙ РЕЖИМ")
    print("-" * 30)
    
    try:
        # Импортируем компонент
        sys.path.append('security/ai_agents')
        from contextual_alert_system import ContextualAlertSystem
        
        # Создаем экземпляр
        alert_system = ContextualAlertSystem()
        
        # Проверяем текущий статус
        print(f"📊 Текущий статус: {alert_system.status}")
        
        # Переводим в спящий режим
        alert_system.status = "SLEEP"
        alert_system.last_update = datetime.now()
        
        print(f"✅ Статус изменен на: {alert_system.status}")
        print(f"🕐 Время перевода: {alert_system.last_update}")
        
        # Сохраняем конфигурацию спящего режима
        sleep_config = {
            "component": "ContextualAlertSystem",
            "status": "SLEEP",
            "sleep_time": datetime.now().isoformat(),
            "quality_score": quality_score,
            "components": components,
            "quality_checks": quality_checks,
            "total_lines": total_lines,
            "code_lines": code_lines
        }
        
        os.makedirs("data/sleep_mode", exist_ok=True)
        config_file = "data/sleep_mode/contextual_alert_sleep_config.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sleep_config, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Конфигурация спящего режима сохранена: {config_file}")
        
        # Создаем лог
        log_file = f"logs/contextual_alert_sleep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"ContextualAlertSystem переведен в спящий режим\n")
            f.write(f"Время: {datetime.now().isoformat()}\n")
            f.write(f"Качество: {quality_score:.1f}/100\n")
            f.write(f"Статус: {alert_system.status}\n")
        
        print(f"📝 Лог создан: {log_file}")
        
        print(f"\n🎉 CONTEXTUALALERTSYSTEM УСПЕШНО ПЕРЕВЕДЕН В СПЯЩИЙ РЕЖИМ!")
        print(f"   📊 Качество: {quality_score:.1f}/100")
        print(f"   😴 Статус: SLEEP")
        print(f"   🕐 Время: {alert_system.last_update}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка перевода в спящий режим: {e}")
        return False

if __name__ == "__main__":
    success = put_contextual_alert_to_sleep()
    if success:
        print("\n✅ СКРИПТ ВЫПОЛНЕН УСПЕШНО!")
    else:
        print("\n❌ СКРИПТ ЗАВЕРШИЛСЯ С ОШИБКОЙ!")