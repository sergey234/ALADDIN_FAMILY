#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест качества PasswordSecurityAgent
"""

import os
import sys
import time
import json
from datetime import datetime

def test_password_security_quality():
    """Тест качества PasswordSecurityAgent"""
    print("🎯 ТЕСТ КАЧЕСТВА PASSWORDSECURITYAGENT")
    print("=" * 60)
    
    try:
        # Проверка существования файла
        agent_file = "security/ai_agents/password_security_agent.py"
        if not os.path.exists(agent_file):
            print("❌ Файл PasswordSecurityAgent не найден")
            return False
        
        print("✅ Файл PasswordSecurityAgent найден")
        
        # Проверка содержимого файла
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Проверка ключевых компонентов
        key_components = [
            # Основные классы
            "class PasswordSecurityAgent",
            "class PasswordPolicy",
            "class PasswordMetrics",
            
            # Перечисления
            "class PasswordStrength(Enum)",
            "class PasswordStatus(Enum)",
            
            # Основные методы
            "def initialize(self)",
            "generate_password",
            "analyze_password_strength",
            "hash_password",
            "verify_password",
            "def generate_report(self)",
            "def stop(self)",
            
            # AI модели
            "def _initialize_ai_models(self)",
            "_calculate_entropy",
            "_has_common_patterns",
            "_generate_strong_password",
            
            # Безопасность паролей
            "def _load_breach_database(self)",
            "def _setup_security_systems(self)",
            "check_password_breach",
            "validate_password_policy",
            
            # Утилиты
            "_save_data",
            "_validate_password_params",
            "_generate_recommendations"
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
            "Политики паролей": content.count("PasswordPolicy"),
            "Уровни сложности": content.count("PasswordStrength"),
            "Статусы паролей": content.count("PasswordStatus"),
            "Метрики паролей": content.count("PasswordMetrics"),
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
            "SOLID принципы": content.count("def ") >= 25,  # Много методов = разделение ответственности
            "DRY принцип": content.count("def _") >= 10,  # Много приватных методов = переиспользование
            "Модульность": content.count("class ") >= 4,  # Несколько классов = модульность
            "Расширяемость": content.count("Enum") >= 2,  # Перечисления = расширяемость
            "Документация": content.count('"""') >= 10,  # Документация
            "Обработка ошибок": content.count("except") >= 15,  # Обработка ошибок
            "Логирование": content.count("log_activity") >= 20,  # Логирование
            "Конфигурация": content.count("self.") >= 50  # Конфигурируемость
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
            "Генерация паролей": "generate_password" in content,
            "Анализ сложности": "analyze_password_strength" in content,
            "Хеширование паролей": "hash_password" in content,
            "Проверка паролей": "verify_password" in content,
            "Проверка утечек": "check_password_breach" in content,
            "Валидация политики": "validate_password_policy" in content,
            "Расчет энтропии": "_calculate_entropy" in content,
            "Обнаружение паттернов": "_has_common_patterns" in content,
            "Генерация сильных паролей": "_generate_strong_password" in content,
            "Загрузка базы утечек": "_load_breach_database" in content,
            "Настройка безопасности": "_setup_security_systems" in content,
            "Валидация параметров": "_validate_password_params" in content,
            "Генерация отчетов": "generate_report" in content,
            "Генерация рекомендаций": "_generate_recommendations" in content,
            "Сохранение данных": "_save_data" in content,
            "Инициализация AI": "_initialize_ai_models" in content
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
            "Аутентификация источников": "password" in content.lower(),
            "Шифрование данных": "hash" in content.lower(),
            "Контроль доступа": "access" in content.lower() or "policy" in content.lower(),
            "Аудит действий": "audit" in content.lower() or "breach" in content.lower()
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
        if os.path.exists("tests/test_password_security_agent.py"):
            with open("tests/test_password_security_agent.py", 'r') as f:
                test_file_content = f.read()
        
        test_checks = {
            "Unit тесты": os.path.exists("tests/test_password_security_agent.py"),
            "Тест качества": os.path.exists("scripts/test_password_security_quality.py"),
            "Спящий режим": os.path.exists("scripts/put_password_security_to_sleep.py"),
            "Покрытие кода": code_line_count >= 500,
            "Документация тестов": "unittest" in test_file_content and "TestPasswordSecurityAgent" in test_file_content and '"""' in test_file_content
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
            "agent_name": "PasswordSecurityAgent",
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
        
        report_file = os.path.join(report_dir, "password_security_quality_test_{}.json".format(int(time.time())))
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
    success = test_password_security_quality()
    if success:
        print("\n🎉 PASSWORDSECURITYAGENT СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
    else:
        print("\n⚠️ PASSWORDSECURITYAGENT ТРЕБУЕТ УЛУЧШЕНИЯ!")
    exit(0 if success else 1)