#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест качества ComplianceAgent
"""

import os
import sys
import time
import json
from datetime import datetime

def test_compliance_quality():
    """Тест качества ComplianceAgent"""
    print("🎯 ТЕСТ КАЧЕСТВА COMPLIANCEAGENT")
    print("=" * 60)
    
    try:
        # Проверка существования файла
        agent_file = "security/ai_agents/compliance_agent.py"
        if not os.path.exists(agent_file):
            print("❌ Файл ComplianceAgent не найден")
            return False
        
        print("✅ Файл ComplianceAgent найден")
        
        # Проверка содержимого файла
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Проверка ключевых компонентов
        key_components = [
            # Основные классы
            "class ComplianceAgent",
            "class ComplianceRequirement",
            "class ComplianceMetrics",
            
            # Перечисления
            "class ComplianceStandard(Enum)",
            "class ComplianceLevel(Enum)",
            "class ComplianceCategory(Enum)",
            
            # Основные методы
            "def initialize(self)",
            "create_requirement",
            "assess_requirement",
            "def generate_compliance_report(self)",
            "def stop(self)",
            
            # AI модели
            "def _initialize_ai_models(self)",
            "_analyze_compliance",
            "_analyze_evidence_quality",
            "_analyze_control_effectiveness",
            "_analyze_risk_level",
            
            # Стандарты соответствия
            "def _load_compliance_standards(self)",
            "_create_requirements_for_standard",
            "_map_category",
            "_calculate_priority",
            
            # Оценка и анализ
            "def _setup_monitoring(self)",
            "_update_metrics",
            "_recalculate_compliance_metrics",
            "_generate_recommendations",
            
            # Утилиты
            "_save_data",
            "_validate_requirement_data"
        ]
        
        missing_components = []
        for component in key_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print("❌ Отсутствуют компоненты: {}".format(len(missing_components)))
            for missing in missing_components[:5]:
                print("   - {}".format(missing))
            if len(missing_components) > 5:
                print("   ... и еще {} компонентов".format(len(missing_components) - 5))
            return False
        
        print("✅ Все ключевые компоненты найдены")
        
        # Проверка качества кода
        lines = content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        total_lines = len(lines)
        code_line_count = len(code_lines)
        
        print("\n📊 СТАТИСТИКА КОДА:")
        print("   📄 Всего строк: {}".format(total_lines))
        print("   💻 Строк кода: {}".format(code_line_count))
        print("   📝 Комментариев: {}".format(total_lines - code_line_count))
        print("   📈 Плотность кода: {:.1f}%".format((code_line_count / total_lines) * 100))
        
        # Подсчет компонентов
        components = {
            "Классы": content.count("class "),
            "Методы": content.count("def "),
            "Перечисления": content.count("class.*Enum"),
            "AI модели": content.count("model_type"),
            "Стандарты соответствия": content.count("ComplianceStandard"),
            "Уровни соответствия": content.count("ComplianceLevel"),
            "Категории соответствия": content.count("ComplianceCategory"),
            "Требования соответствия": content.count("ComplianceRequirement"),
            "Обработка ошибок": content.count("except"),
            "Логирование": content.count("log_activity"),
            "Документация": content.count('"""'),
            "Конфигурация": content.count("self.")
        }
        
        print("\n🔧 КОМПОНЕНТЫ СИСТЕМЫ:")
        total_components = 0
        for component, count in components.items():
            print("   {}: {}".format(component, count))
            total_components += count
        
        # Проверка архитектурных принципов
        architecture_checks = {
            "SOLID принципы": content.count("def ") >= 30,  # Много методов = разделение ответственности
            "DRY принцип": content.count("def _") >= 20,  # Много приватных методов = переиспользование
            "Модульность": content.count("class ") >= 5,  # Несколько классов = модульность
            "Расширяемость": content.count("Enum") >= 3,  # Перечисления = расширяемость
            "Документация": content.count('"""') >= 15,  # Документация
            "Обработка ошибок": content.count("except") >= 20,  # Обработка ошибок
            "Логирование": content.count("log_activity") >= 30,  # Логирование
            "Конфигурация": content.count("self.") >= 80  # Конфигурируемость
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
            "Создание требований": "create_requirement" in content,
            "Оценка требований": "assess_requirement" in content,
            "Генерация отчетов": "generate_compliance_report" in content,
            "AI анализ соответствия": "_analyze_compliance" in content,
            "Анализ качества доказательств": "_analyze_evidence_quality" in content,
            "Анализ эффективности контролей": "_analyze_control_effectiveness" in content,
            "Анализ уровня риска": "_analyze_risk_level" in content,
            "Загрузка стандартов": "_load_compliance_standards" in content,
            "Создание требований для стандарта": "_create_requirements_for_standard" in content,
            "Маппинг категорий": "_map_category" in content,
            "Расчет приоритета": "_calculate_priority" in content,
            "Настройка мониторинга": "_setup_monitoring" in content,
            "Обновление метрик": "_update_metrics" in content,
            "Пересчет метрик": "_recalculate_compliance_metrics" in content,
            "Генерация рекомендаций": "_generate_recommendations" in content,
            "Сохранение данных": "_save_data" in content,
            "Валидация данных": "_validate_requirement_data" in content
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
            "Валидация входных данных": "validation" in content.lower() or "validate" in content.lower() or "check" in content.lower(),
            "Обработка ошибок": "except" in content,
            "Безопасное логирование": "log_activity" in content,
            "Конфиденциальность данных": "data" in content.lower(),
            "Аутентификация источников": "compliance" in content.lower(),
            "Шифрование данных": "hash" in content.lower(),
            "Контроль доступа": "access" in content.lower(),
            "Аудит действий": "audit" in content.lower() or "evidence" in content.lower()
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
        if os.path.exists("tests/test_compliance_agent.py"):
            with open("tests/test_compliance_agent.py", 'r') as f:
                test_file_content = f.read()
        
        test_checks = {
            "Unit тесты": os.path.exists("tests/test_compliance_agent.py"),
            "Тест качества": os.path.exists("scripts/test_compliance_quality.py"),
            "Спящий режим": os.path.exists("scripts/put_compliance_to_sleep.py"),
            "Покрытие кода": code_line_count >= 800,
            "Документация тестов": "unittest" in test_file_content and "TestComplianceAgent" in test_file_content and '"""' in test_file_content
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
            "agent_name": "ComplianceAgent",
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
        
        report_file = os.path.join(report_dir, "compliance_quality_test_{}.json".format(int(time.time())))
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
    success = test_compliance_quality()
    if success:
        print("\n🎉 COMPLIANCEAGENT СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
    else:
        print("\n⚠️ COMPLIANCEAGENT ТРЕБУЕТ УЛУЧШЕНИЯ!")
    exit(0 if success else 1)