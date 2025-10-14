#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простой тест MobileSecurityAgent без зависимостей
"""

import os
import sys
import time
from datetime import datetime

def test_mobile_security_agent():
    """Простой тест MobileSecurityAgent"""
    print("🧪 ПРОСТОЙ ТЕСТ MobileSecurityAgent")
    print("=" * 50)
    
    try:
        # Проверка существования файла
        agent_file = "security/ai_agents/mobile_security_agent.py"
        if not os.path.exists(agent_file):
            print("❌ Файл MobileSecurityAgent не найден")
            return False
        
        print("✅ Файл MobileSecurityAgent найден")
        
        # Проверка содержимого файла
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Проверка ключевых компонентов
        required_components = [
            "class MobileSecurityAgent",
            "class MobileDevice",
            "class MobileApp", 
            "class MobileThreat",
            "class MobileSecurityMetrics",
            "MobilePlatform",
            "DeviceType",
            "ThreatType",
            "SecurityStatus",
            "AppPermission"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print("❌ Отсутствуют компоненты: {}".format(", ".join(missing_components)))
            return False
        
        print("✅ Все ключевые компоненты найдены")
        
        # Проверка методов
        required_methods = [
            "def __init__",
            "def initialize",
            "def register_device",
            "def scan_device",
            "def get_device_security_report",
            "def get_system_metrics",
            "def stop"
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print("❌ Отсутствуют методы: {}".format(", ".join(missing_methods)))
            return False
        
        print("✅ Все ключевые методы найдены")
        
        # Проверка AI моделей
        ai_components = [
            "threat_classifier",
            "app_analyzer", 
            "behavior_analyzer",
            "permission_analyzer"
        ]
        
        missing_ai = []
        for ai_component in ai_components:
            if ai_component not in content:
                missing_ai.append(ai_component)
        
        if missing_ai:
            print("❌ Отсутствуют AI компоненты: {}".format(", ".join(missing_ai)))
            return False
        
        print("✅ Все AI компоненты найдены")
        
        # Проверка баз данных угроз
        threat_databases = [
            "malware_signatures",
            "phishing_patterns",
            "vulnerability_database",
            "trusted_apps_database",
            "suspicious_apps_database"
        ]
        
        missing_databases = []
        for database in threat_databases:
            if database not in content:
                missing_databases.append(database)
        
        if missing_databases:
            print("❌ Отсутствуют базы данных: {}".format(", ".join(missing_databases)))
            return False
        
        print("✅ Все базы данных угроз найдены")
        
        # Проверка функций безопасности
        security_functions = [
            "_check_device_encryption",
            "_check_root_jailbreak",
            "_scan_installed_apps",
            "_analyze_app_permissions",
            "_analyze_network_behavior",
            "_analyze_device_behavior",
            "_calculate_security_score"
        ]
        
        missing_functions = []
        for function in security_functions:
            if function not in content:
                missing_functions.append(function)
        
        if missing_functions:
            print("❌ Отсутствуют функции безопасности: {}".format(", ".join(missing_functions)))
            return False
        
        print("✅ Все функции безопасности найдены")
        
        # Проверка документации
        doc_indicators = [
            '"""',
            "Автор: ALADDIN Security Team",
            "Версия: 1.0",
            "Дата: 2025-01-03"
        ]
        
        missing_docs = []
        for doc in doc_indicators:
            if doc not in content:
                missing_docs.append(doc)
        
        if missing_docs:
            print("⚠️ Неполная документация: {}".format(", ".join(missing_docs)))
        else:
            print("✅ Документация полная")
        
        # Проверка обработки ошибок
        error_handling = [
            "try:",
            "except Exception as e:",
            "self.log_activity"
        ]
        
        missing_error_handling = []
        for error_component in error_handling:
            if error_component not in content:
                missing_error_handling.append(error_component)
        
        if missing_error_handling:
            print("⚠️ Неполная обработка ошибок: {}".format(", ".join(missing_error_handling)))
        else:
            print("✅ Обработка ошибок полная")
        
        # Подсчет строк кода
        lines = content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        total_lines = len(lines)
        code_line_count = len(code_lines)
        
        print("\n📊 СТАТИСТИКА КОДА:")
        print("   📄 Всего строк: {}".format(total_lines))
        print("   💻 Строк кода: {}".format(code_line_count))
        print("   📝 Комментариев: {}".format(total_lines - code_line_count))
        
        # Проверка качества кода
        quality_score = 0
        max_score = 100
        
        # Базовые компоненты (30 баллов)
        if len(missing_components) == 0:
            quality_score += 30
        else:
            quality_score += 30 - len(missing_components) * 3
        
        # Методы (25 баллов)
        if len(missing_methods) == 0:
            quality_score += 25
        else:
            quality_score += 25 - len(missing_methods) * 3
        
        # AI компоненты (20 баллов)
        if len(missing_ai) == 0:
            quality_score += 20
        else:
            quality_score += 20 - len(missing_ai) * 5
        
        # Функции безопасности (15 баллов)
        if len(missing_functions) == 0:
            quality_score += 15
        else:
            quality_score += 15 - len(missing_functions) * 2
        
        # Документация (5 баллов)
        if len(missing_docs) == 0:
            quality_score += 5
        else:
            quality_score += 5 - len(missing_docs)
        
        # Обработка ошибок (5 баллов)
        if len(missing_error_handling) == 0:
            quality_score += 5
        else:
            quality_score += 5 - len(missing_error_handling)
        
        print("\n🏆 ОЦЕНКА КАЧЕСТВА: {}/{}".format(quality_score, max_score))
        
        if quality_score >= 90:
            print("✅ КАЧЕСТВО: A+ (ОТЛИЧНО)")
        elif quality_score >= 80:
            print("✅ КАЧЕСТВО: A (ХОРОШО)")
        elif quality_score >= 70:
            print("⚠️ КАЧЕСТВО: B (УДОВЛЕТВОРИТЕЛЬНО)")
        else:
            print("❌ КАЧЕСТВО: C (ТРЕБУЕТ УЛУЧШЕНИЯ)")
        
        return quality_score >= 80
        
    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: {}".format(str(e)))
        return False


if __name__ == "__main__":
    success = test_mobile_security_agent()
    if success:
        print("\n🎉 ТЕСТ MOBILESECURITYAGENT ПРОЙДЕН УСПЕШНО!")
    else:
        print("\n❌ ТЕСТ MOBILESECURITYAGENT НЕ ПРОЙДЕН!")
    exit(0 if success else 1)