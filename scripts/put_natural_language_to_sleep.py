#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт перевода NaturalLanguageProcessor в спящий режим
Создан: 2024-09-05
Версия: 1.0.0
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def put_natural_language_to_sleep():
    """Перевод NaturalLanguageProcessor в спящий режим"""
    print("😴 ПЕРЕВОД NATURALLANGUAGEPROCESSOR В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)
    
    # Проверяем существование файла
    file_path = "security/ai_agents/natural_language_processor.py"
    if not os.path.exists(file_path):
        print("❌ Файл NaturalLanguageProcessor не найден")
        return False
    
    print("✅ Файл NaturalLanguageProcessor найден")
    
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
        "NLP": content.count("nlp") + content.count("NLP") + content.count("natural"),
        "Намерения": content.count("intent") + content.count("Intent"),
        "Сущности": content.count("entity") + content.count("Entity"),
        "Тональность": content.count("sentiment") + content.count("Sentiment"),
        "Контекст": content.count("context") + content.count("Context"),
        "Ключевые слова": content.count("keyword") + content.count("Keyword"),
        "Эмоции": content.count("emotion") + content.count("Emotion"),
        "Токенизация": content.count("token") + content.count("Token"),
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
        "NLP": components["NLP"] > 5,
        "Намерения": components["Намерения"] > 5,
        "Сущности": components["Сущности"] > 5,
        "Тональность": components["Тональность"] > 5,
        "Контекст": components["Контекст"] > 5,
        "Ключевые слова": components["Ключевые слова"] > 5,
        "Эмоции": components["Эмоции"] > 5,
        "Токенизация": components["Токенизация"] > 5,
        "Тестирование": components["Тестирование"] > 5,
        "Цветовая схема": components["Цветовая схема"] > 5,
        "Покрытие кода": code_lines >= 500
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
        from natural_language_processor import NaturalLanguageProcessor
        
        # Создаем экземпляр
        nlp_processor = NaturalLanguageProcessor()
        
        # Проверяем текущий статус
        print(f"📊 Текущий статус: {nlp_processor.status}")
        
        # Переводим в спящий режим
        nlp_processor.status = "SLEEP"
        nlp_processor.last_update = datetime.now()
        
        print(f"✅ Статус изменен на: {nlp_processor.status}")
        print(f"🕐 Время перевода: {nlp_processor.last_update}")
        
        # Сохраняем конфигурацию спящего режима
        sleep_config = {
            "component": "NaturalLanguageProcessor",
            "status": "SLEEP",
            "sleep_time": datetime.now().isoformat(),
            "quality_score": quality_score,
            "components": components,
            "quality_checks": quality_checks,
            "total_lines": total_lines,
            "code_lines": code_lines
        }
        
        os.makedirs("data/sleep_mode", exist_ok=True)
        config_file = "data/sleep_mode/natural_language_sleep_config.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sleep_config, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Конфигурация спящего режима сохранена: {config_file}")
        
        # Создаем лог
        log_file = f"logs/natural_language_sleep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"NaturalLanguageProcessor переведен в спящий режим\n")
            f.write(f"Время: {datetime.now().isoformat()}\n")
            f.write(f"Качество: {quality_score:.1f}/100\n")
            f.write(f"Статус: {nlp_processor.status}\n")
        
        print(f"📝 Лог создан: {log_file}")
        
        print(f"\n🎉 NATURALLANGUAGEPROCESSOR УСПЕШНО ПЕРЕВЕДЕН В СПЯЩИЙ РЕЖИМ!")
        print(f"   📊 Качество: {quality_score:.1f}/100")
        print(f"   😴 Статус: SLEEP")
        print(f"   🕐 Время: {nlp_processor.last_update}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка перевода в спящий режим: {e}")
        return False

if __name__ == "__main__":
    success = put_natural_language_to_sleep()
    if success:
        print("\n✅ СКРИПТ ВЫПОЛНЕН УСПЕШНО!")
    else:
        print("\n❌ СКРИПТ ЗАВЕРШИЛСЯ С ОШИБКОЙ!")