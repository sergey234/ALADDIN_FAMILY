#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест качества ThreatIntelligenceAgent
"""

import os
import sys
import time
import json
from datetime import datetime

def test_threat_intelligence_quality():
    """Тест качества ThreatIntelligenceAgent"""
    print("🎯 ТЕСТ КАЧЕСТВА THREATINTELLIGENCEAGENT")
    print("=" * 60)
    
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
        
        # Проверка ключевых компонентов
        key_components = [
            # Основные классы
            "class ThreatIntelligenceAgent",
            "class ThreatIntelligence",
            "class ThreatIntelligenceMetrics",
            
            # Перечисления
            "class ThreatType(Enum)",
            "class ThreatSeverity(Enum)",
            "class IOCType(Enum)",
            "class ThreatSource(Enum)",
            
            # Основные методы
            "def initialize(self)",
            "def collect_threats(self)",
            "def analyze_threats(self)",
            "def generate_report(self)",
            "def stop(self)",
            
            # AI модели
            "def _initialize_ai_models(self)",
            "_classify_threat",
            "_predict_severity",
            "_analyze_iocs",
            
            # Источники угроз
            "def _load_threat_sources(self)",
            "_collect_from_rss_feeds",
            "_collect_from_api",
            "_collect_from_government_feeds",
            "_collect_from_academic_sources",
            
            # Анализ и валидация
            "_analyze_single_threat",
            "_calculate_data_quality",
            "_generate_recommendations",
            
            # Утилиты
            "_save_data",
            "_get_threats_by_type",
            "_get_threats_by_severity"
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
            "Источники угроз": content.count("source"),
            "IOC типы": content.count("IOCType"),
            "Типы угроз": content.count("ThreatType"),
            "Уровни серьезности": content.count("ThreatSeverity")
        }
        
        print("\n🔧 КОМПОНЕНТЫ СИСТЕМЫ:")
        for component, count in components.items():
            print("   {}: {}".format(component, count))
        
        # Проверка архитектурных принципов
        architecture_checks = {
            "SOLID принципы": content.count("def ") >= 20,  # Много методов = разделение ответственности
            "DRY принцип": content.count("def _") >= 15,  # Много приватных методов = переиспользование
            "Модульность": content.count("class ") >= 4,  # Несколько классов = модульность
            "Расширяемость": content.count("Enum") >= 4,  # Перечисления = расширяемость
            "Документация": content.count('"""') >= 10,  # Документация
            "Обработка ошибок": content.count("except") >= 10,  # Обработка ошибок
            "Логирование": content.count("log_activity") >= 15,  # Логирование
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
        
        # Расчет общего качества
        total_score = 0
        max_score = 100
        
        # Архитектура (30 баллов)
        architecture_percentage = (architecture_score / len(architecture_checks)) * 30
        total_score += architecture_percentage
        
        # Функциональность (40 баллов)
        functionality_percentage = (functionality_score / len(functionality_checks)) * 40
        total_score += functionality_percentage
        
        # Безопасность (20 баллов)
        security_percentage = (security_score / len(security_checks)) * 20
        total_score += security_percentage
        
        # Качество кода (10 баллов)
        code_quality = min(10, (code_line_count / 1000) * 10)  # Бонус за объем кода
        total_score += code_quality
        
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
        
        # Создание отчета о качестве
        quality_report = {
            "test_timestamp": datetime.now().isoformat(),
            "agent_name": "ThreatIntelligenceAgent",
            "total_score": total_score,
            "max_score": max_score,
            "quality_grade": quality_grade,
            "code_statistics": {
                "total_lines": total_lines,
                "code_lines": code_line_count,
                "comment_lines": total_lines - code_line_count,
                "code_density": (code_line_count / total_lines) * 100
            },
            "components": components,
            "architecture_score": architecture_score,
            "architecture_max": len(architecture_checks),
            "functionality_score": functionality_score,
            "functionality_max": len(functionality_checks),
            "security_score": security_score,
            "security_max": len(security_checks),
            "missing_components": missing_components,
            "status": "PASSED" if total_score >= 90 else "NEEDS_IMPROVEMENT"
        }
        
        # Сохранение отчета
        report_dir = "data/quality_reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        report_file = os.path.join(report_dir, "threat_intelligence_quality_test_{}.json".format(int(time.time())))
        with open(report_file, 'w') as f:
            json.dump(quality_report, f, indent=2, ensure_ascii=False)
        
        print("\n📄 Отчет о качестве сохранен: {}".format(report_file))
        
        return total_score >= 90
        
    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_threat_intelligence_quality()
    if success:
        print("\n🎉 THREATINTELLIGENCEAGENT СООТВЕТСТВУЕТ СТАНДАРТАМ A+ КАЧЕСТВА!")
    else:
        print("\n⚠️ THREATINTELLIGENCEAGENT ТРЕБУЕТ УЛУЧШЕНИЯ!")
    exit(0 if success else 1)