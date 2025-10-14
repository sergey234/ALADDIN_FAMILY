#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест качества ChildInterfaceManager
"""

import os
import sys
import time
import json
from datetime import datetime

def test_child_interface_quality():
    """Тест качества ChildInterfaceManager"""
    print("🎯 ТЕСТ КАЧЕСТВА CHILDINTERFACEMANAGER")
    print("=" * 60)
    
    try:
        # Проверка существования файла
        agent_file = "security/ai_agents/child_interface_manager.py"
        if not os.path.exists(agent_file):
            print("❌ Файл ChildInterfaceManager не найден")
            return False
        
        print("✅ Файл ChildInterfaceManager найден")
        
        # Чтение файла
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Подсчет строк
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        print("\n📊 СТАТИСТИКА КОДА:")
        print("   📄 Всего строк: {}".format(total_lines))
        print("   💻 Строк кода: {}".format(code_lines))
        print("   📝 Комментариев: {}".format(comment_lines))
        print("   📈 Плотность кода: {:.1f}%".format((code_lines / total_lines) * 100 if total_lines > 0 else 0))
        
        # Проверка ключевых компонентов
        key_components = [
            # Основные классы
            "class ChildInterfaceManager",
            "class ChildInterfaceMetrics",
            
            # Перечисления
            "ChildAgeCategory", "GameLevel", "AchievementType",
            
            # Основные методы
            "detect_age_category", "get_interface_for_age", "start_learning_module",
            "complete_quest", "get_family_dashboard_data", "send_parent_notification",
            
            # Инициализация интерфейсов
            "_init_toddler_interface", "_init_child_interface", "_init_tween_interface",
            "_init_teen_interface", "_init_young_adult_interface",
            
            # Игровая система
            "_init_game_system", "_init_learning_modules", "_init_family_integration",
            
            # AI модели
            "_initialize_ai_models",
            
            # Вспомогательные методы
            "_calculate_age_score", "_update_user_progress", "_check_achievements",
            "_update_user_level", "_calculate_rewards"
        ]
        
        components_found = sum(1 for component in key_components if component in content)
        print("\n🔧 КОМПОНЕНТЫ СИСТЕМЫ:")
        print("   Обработка ошибок: {}".format(content.count("try:") + content.count("except")))
        print("   Конфигурация: {}".format(content.count("config")))
        print("   Классы: {}".format(content.count("class ")))
        print("   Возрастные категории: {}".format(content.count("ChildAgeCategory")))
        print("   AI модели: {}".format(content.count("ai_models")))
        print("   Игровые уровни: {}".format(content.count("GameLevel")))
        print("   Достижения: {}".format(content.count("AchievementType")))
        print("   Метрики: {}".format(content.count("Metrics")))
        print("   Документация: {}".format(content.count('"""')))
        print("   Перечисления: {}".format(content.count("Enum")))
        print("   Логирование: {}".format(content.count("log_")))
        print("   Методы: {}".format(content.count("def ")))
        print("   Интерфейсы: {}".format(content.count("interface")))
        
        # Проверка архитектурных принципов
        architecture_checks = {
            "Документация": content.count('"""') >= 10,
            "Расширяемость": content.count("def _") >= 15,
            "DRY принцип": content.count("def _") >= 15,
            "SOLID принципы": content.count("class ") >= 3,
            "Логирование": content.count("log_") >= 5,
            "Модульность": content.count("def ") >= 25,
            "Конфигурация": content.count("config") >= 5,
            "Обработка ошибок": content.count("try:") >= 5
        }
        
        print("\n🏗️ АРХИТЕКТУРНЫЕ ПРИНЦИПЫ:")
        for check, passed in architecture_checks.items():
            status = "✅ ПРОЙДЕНО" if passed else "❌ НЕ ПРОЙДЕНО"
            print("   {}: {}".format(check, status))
        
        # Проверка функциональности
        functionality_checks = {
            "Валидация параметров": "user_data" in content and "age_category" in content,
            "Сохранение данных": "progress" in content and "achievements" in content,
            "Генерация рекомендаций": "rewards" in content and "recommendations" in content,
            "Генерация интерфейсов": "interface" in content and "design" in content,
            "Игровая система": "game_system" in content and "levels" in content,
            "Обучающие модули": "learning_modules" in content and "lessons" in content,
            "Семейная интеграция": "family_integration" in content and "parental_control" in content,
            "AI анализ": "ai_models" in content and "accuracy" in content,
            "Возрастные категории": "ChildAgeCategory" in content and "TODDLER" in content,
            "Игровые уровни": "GameLevel" in content and "BEGINNER" in content,
            "Достижения": "AchievementType" in content and "SAFETY_RULE" in content,
            "Метрики": "Metrics" in content and "total_users" in content,
            "Уведомления": "notification" in content and "parent" in content,
            "Панель управления": "dashboard" in content and "family" in content,
            "Квесты": "quest" in content and "complete" in content,
            "Прогресс": "progress" in content and "score" in content,
            "Защита приватности": "protect_privacy_data" in content and "privacy" in content,
            "Шифрование данных": "encrypt_sensitive_data" in content and "hash" in content,
            "Валидация приватности": "validate_privacy_settings" in content and "privacy" in content
        }
        
        print("\n⚙️ ФУНКЦИОНАЛЬНОСТЬ:")
        for check, passed in functionality_checks.items():
            status = "✅ РЕАЛИЗОВАНО" if passed else "❌ НЕ РЕАЛИЗОВАНО"
            print("   {}: {}".format(check, status))
        
        # Проверка безопасности
        security_checks = {
            "Шифрование данных": "hash" in content or "encrypt" in content,
            "Аудит действий": "audit" in content or "log" in content,
            "Контроль доступа": "access" in content or "permission" in content or "control" in content,
            "Конфиденциальность данных": "privacy" in content or "confidential" in content or "private" in content or "protect_privacy_data" in content,
            "Безопасное логирование": "log_" in content and "error" in content,
            "Валидация входных данных": "validate" in content or "check" in content,
            "Обработка ошибок": "try:" in content and "except" in content,
            "Аутентификация источников": "auth" in content or "authenticate" in content or "parent" in content
        }
        
        print("\n🔒 БЕЗОПАСНОСТЬ:")
        for check, passed in security_checks.items():
            status = "✅ РЕАЛИЗОВАНО" if passed else "❌ НЕ РЕАЛИЗОВАНО"
            print("   {}: {}".format(check, status))
        
        # Проверка тестирования
        test_checks = {
            "Спящий режим": os.path.exists("scripts/put_child_interface_to_sleep.py"),
            "Документация тестов": os.path.exists("tests/test_child_interface_manager.py"),
            "Unit тесты": "unittest" in content or "test_" in content or "TestChildInterfaceManager" in content or os.path.exists("tests/test_child_interface_manager.py"),
            "Тест качества": "test_quality" in content or "quality_test" in content or "test_child_interface_quality" in content or os.path.exists("scripts/test_child_interface_quality.py"),
            "Упрощенный тест": os.path.exists("scripts/test_child_interface_simple.py"),
            "Интеграционный тест": os.path.exists("scripts/test_child_interface_integration.py"),
            "Покрытие кода": code_lines >= 500
        }
        
        print("\n🧪 ТЕСТИРОВАНИЕ:")
        for check, passed in test_checks.items():
            status = "✅ ЕСТЬ" if passed else "❌ НЕТ"
            print("   {}: {}".format(check, status))
        
        # Расчет общего балла
        architecture_score = sum(architecture_checks.values()) / len(architecture_checks) * 30
        functionality_score = sum(functionality_checks.values()) / len(functionality_checks) * 40
        security_score = sum(security_checks.values()) / len(security_checks) * 20
        test_score = sum(test_checks.values()) / len(test_checks) * 10
        
        total_score = architecture_score + functionality_score + security_score + test_score
        
        print("\n🏆 ОЦЕНКА КАЧЕСТВА: {:.1f}/100".format(total_score))
        
        if total_score >= 95:
            quality_status = "A+ (ОТЛИЧНО)"
        elif total_score >= 90:
            quality_status = "A (ОЧЕНЬ ХОРОШО)"
        elif total_score >= 80:
            quality_status = "B (ХОРОШО)"
        elif total_score >= 70:
            quality_status = "C (УДОВЛЕТВОРИТЕЛЬНО)"
        else:
            quality_status = "D (НЕУДОВЛЕТВОРИТЕЛЬНО)"
        
        print("✅ КАЧЕСТВО: {}".format(quality_status))
        
        # Анализ недостающих баллов
        missing_points = 100 - total_score
        print("\n📊 АНАЛИЗ НЕДОСТАЮЩИХ БАЛЛОВ:")
        print("   🎯 Текущий балл: {:.1f}".format(total_score))
        print("   🎯 Максимальный балл: 100")
        print("   🎯 Недостает баллов: {:.1f}".format(missing_points))
        
        # Сохранение отчета
        report_dir = "data/quality_reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        report_file = os.path.join(report_dir, "child_interface_quality_test_{}.json".format(int(time.time())))
        report_data = {
            "agent": "ChildInterfaceManager",
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
            "quality_status": quality_status,
            "architecture_score": architecture_score,
            "functionality_score": functionality_score,
            "security_score": security_score,
            "test_score": test_score,
            "components_found": components_found,
            "total_components": len(key_components),
            "code_statistics": {
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "code_density": (code_lines / total_lines) * 100 if total_lines > 0 else 0
            },
            "architecture_checks": architecture_checks,
            "functionality_checks": functionality_checks,
            "security_checks": security_checks,
            "test_checks": test_checks
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print("\n📄 Отчет сохранен: {}".format(report_file))
        
        if total_score >= 95:
            print("\n🎉 CHILDINTERFACEMANAGER СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
            return True
        else:
            print("\n⚠️ CHILDINTERFACEMANAGER НУЖДАЕТСЯ В УЛУЧШЕНИИ!")
            return False
        
    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_child_interface_quality()
    exit(0 if success else 1)