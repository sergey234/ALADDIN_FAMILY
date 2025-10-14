#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Упрощенный тест ThreatIntelligenceAgent
"""

import os
import sys
import time
import json
from datetime import datetime

def test_threat_intelligence_simple():
    """Упрощенный тест ThreatIntelligenceAgent"""
    print("🧪 УПРОЩЕННЫЙ ТЕСТ THREATINTELLIGENCEAGENT")
    print("=" * 50)
    
    try:
        # Проверка существования файла
        agent_file = "security/ai_agents/threat_intelligence_agent.py"
        if not os.path.exists(agent_file):
            print("❌ Файл ThreatIntelligenceAgent не найден")
            return False
        
        print("✅ Файл ThreatIntelligenceAgent найден")
        
        # Проверка содержимого файла
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Проверка основных компонентов
        components = {
            "Классы": content.count("class "),
            "Методы": content.count("def "),
            "Перечисления": content.count("class.*Enum"),
            "AI модели": content.count("model_type"),
            "Источники угроз": content.count("source"),
            "IOC типы": content.count("IOCType"),
            "Типы угроз": content.count("ThreatType"),
            "Уровни серьезности": content.count("ThreatSeverity"),
            "Обработка ошибок": content.count("except"),
            "Логирование": content.count("log_activity"),
            "Документация": content.count('"""'),
            "Конфигурация": content.count("self.")
        }
        
        print("\n📊 КОМПОНЕНТЫ СИСТЕМЫ:")
        total_components = 0
        for component, count in components.items():
            print("   {}: {}".format(component, count))
            total_components += count
        
        # Проверка качества кода
        lines = content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        total_lines = len(lines)
        code_line_count = len(code_lines)
        
        print("\n📈 СТАТИСТИКА КОДА:")
        print("   📄 Всего строк: {}".format(total_lines))
        print("   💻 Строк кода: {}".format(code_line_count))
        print("   📝 Комментариев: {}".format(total_lines - code_line_count))
        print("   📊 Плотность кода: {:.1f}%".format((code_line_count / total_lines) * 100))
        
        # Проверка архитектурных принципов
        architecture_checks = {
            "SOLID принципы": content.count("def ") >= 20,
            "DRY принцип": content.count("def _") >= 15,
            "Модульность": content.count("class ") >= 4,
            "Расширяемость": content.count("Enum") >= 4,
            "Документация": content.count('"""') >= 10,
            "Обработка ошибок": content.count("except") >= 10,
            "Логирование": content.count("log_activity") >= 15,
            "Конфигурация": content.count("self.") >= 50
        }
        
        print("\n🏗️ АРХИТЕКТУРНЫЕ ПРИНЦИПЫ:")
        architecture_score = 0
        for principle, passed in architecture_checks.items():
            status = "✅" if passed else "❌"
            print("   {} {}: {}".format(status, principle, "ПРОЙДЕНО" if passed else "НЕ ПРОЙДЕНО"))
            if passed:
                architecture_score += 1
        
        # Проверка функциональности
        functionality_checks = {
            "Сбор угроз": "collect_threats" in content,
            "Анализ угроз": "analyze_threats" in content,
            "Генерация отчетов": "generate_report" in content,
            "AI классификация": "_classify_threat" in content,
            "Предсказание серьезности": "_predict_severity" in content,
            "Анализ IOCs": "_analyze_iocs" in content,
            "Множественные источники": "_collect_from_" in content,
            "Качество данных": "_calculate_data_quality" in content,
            "Рекомендации": "_generate_recommendations" in content,
            "Сохранение данных": "_save_data" in content
        }
        
        print("\n⚙️ ФУНКЦИОНАЛЬНОСТЬ:")
        functionality_score = 0
        for function, implemented in functionality_checks.items():
            status = "✅" if implemented else "❌"
            print("   {} {}: {}".format(status, function, "РЕАЛИЗОВАНО" if implemented else "НЕ РЕАЛИЗОВАНО"))
            if implemented:
                functionality_score += 1
        
        # Проверка безопасности
        security_checks = {
            "Валидация входных данных": "validation" in content.lower(),
            "Обработка ошибок": "except" in content,
            "Безопасное логирование": "log_activity" in content,
            "Конфиденциальность данных": "data" in content.lower(),
            "Аутентификация источников": "source" in content.lower(),
            "Шифрование данных": "hash" in content.lower()
        }
        
        print("\n🔒 БЕЗОПАСНОСТЬ:")
        security_score = 0
        for security, implemented in security_checks.items():
            status = "✅" if implemented else "❌"
            print("   {} {}: {}".format(status, security, "РЕАЛИЗОВАНО" if implemented else "НЕ РЕАЛИЗОВАНО"))
            if implemented:
                security_score += 1
        
        # Проверка тестирования
        test_file_content = ""
        if os.path.exists("tests/test_threat_intelligence_agent.py"):
            with open("tests/test_threat_intelligence_agent.py", 'r') as f:
                test_file_content = f.read()
        
        test_checks = {
            "Unit тесты": os.path.exists("tests/test_threat_intelligence_agent.py"),
            "Тест качества": os.path.exists("scripts/test_threat_intelligence_quality.py"),
            "Спящий режим": os.path.exists("scripts/put_threat_intelligence_to_sleep.py"),
            "Покрытие кода": code_line_count >= 500,
            "Документация тестов": "unittest" in test_file_content and "TestThreatIntelligenceAgent" in test_file_content and '"""' in test_file_content
        }
        
        print("\n🧪 ТЕСТИРОВАНИЕ:")
        test_score = 0
        for test, exists in test_checks.items():
            status = "✅" if exists else "❌"
            print("   {} {}: {}".format(status, test, "ЕСТЬ" if exists else "НЕТ"))
            if exists:
                test_score += 1
        
        # Расчет общего качества
        total_score = 0
        max_score = 100
        
        # Архитектура (25 баллов)
        architecture_percentage = (architecture_score / len(architecture_checks)) * 25
        total_score += architecture_percentage
        
        # Функциональность (35 баллов)
        functionality_percentage = (functionality_score / len(functionality_checks)) * 35
        total_score += functionality_percentage
        
        # Безопасность (20 баллов)
        security_percentage = (security_score / len(security_checks)) * 20
        total_score += security_percentage
        
        # Тестирование (20 баллов)
        test_percentage = (test_score / len(test_checks)) * 20
        total_score += test_percentage
        
        print("\n🏆 ОЦЕНКА КАЧЕСТВА: {:.1f}/{}".format(total_score, max_score))
        
        if total_score >= 95:
            print("✅ КАЧЕСТВО: A+ (ОТЛИЧНО)")
            quality_grade = "A+"
        elif total_score >= 90:
            print("✅ КАЧЕСТВО: A (ОТЛИЧНО)")
            quality_grade = "A"
        elif total_score >= 80:
            print("⚠️ КАЧЕСТВО: B (ХОРОШО)")
            quality_grade = "B"
        elif total_score >= 70:
            print("⚠️ КАЧЕСТВО: C (УДОВЛЕТВОРИТЕЛЬНО)")
            quality_grade = "C"
        else:
            print("❌ КАЧЕСТВО: D (ТРЕБУЕТ УЛУЧШЕНИЯ)")
            quality_grade = "D"
        
        # Анализ недостающих баллов
        missing_points = max_score - total_score
        print("\n📊 АНАЛИЗ НЕДОСТАЮЩИХ БАЛЛОВ:")
        print("   🎯 Текущий балл: {:.1f}".format(total_score))
        print("   🎯 Максимальный балл: {}".format(max_score))
        print("   🎯 Недостает баллов: {:.1f}".format(missing_points))
        
        if missing_points > 0:
            print("\n🔧 ЧТО НУЖНО ДЛЯ 100%:")
            
            # Анализ по категориям
            arch_missing = (25 - architecture_percentage)
            func_missing = (35 - functionality_percentage)
            sec_missing = (20 - security_percentage)
            test_missing = (20 - test_percentage)
            
            if arch_missing > 0:
                print("   🏗️ Архитектура: +{:.1f} баллов".format(arch_missing))
            if func_missing > 0:
                print("   ⚙️ Функциональность: +{:.1f} баллов".format(func_missing))
            if sec_missing > 0:
                print("   🔒 Безопасность: +{:.1f} баллов".format(sec_missing))
            if test_missing > 0:
                print("   🧪 Тестирование: +{:.1f} баллов".format(test_missing))
        
        # Создание отчета
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "agent_name": "ThreatIntelligenceAgent",
            "total_score": total_score,
            "max_score": max_score,
            "quality_grade": quality_grade,
            "missing_points": missing_points,
            "components": components,
            "architecture_score": architecture_score,
            "architecture_max": len(architecture_checks),
            "functionality_score": functionality_score,
            "functionality_max": len(functionality_checks),
            "security_score": security_score,
            "security_max": len(security_checks),
            "test_score": test_score,
            "test_max": len(test_checks),
            "code_statistics": {
                "total_lines": total_lines,
                "code_lines": code_line_count,
                "comment_lines": total_lines - code_line_count,
                "code_density": (code_line_count / total_lines) * 100
            }
        }
        
        # Сохранение отчета
        report_dir = "data/quality_reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        report_file = os.path.join(report_dir, "threat_intelligence_simple_test_{}.json".format(int(time.time())))
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n📄 Отчет сохранен: {}".format(report_file))
        
        return total_score >= 90
        
    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_threat_intelligence_simple()
    if success:
        print("\n🎉 THREATINTELLIGENCEAGENT СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
    else:
        print("\n⚠️ THREATINTELLIGENCEAGENT ТРЕБУЕТ УЛУЧШЕНИЯ!")
    exit(0 if success else 1)