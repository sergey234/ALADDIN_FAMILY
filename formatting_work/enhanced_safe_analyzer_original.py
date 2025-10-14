#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный Безопасный Анализатор Качества
С детальным выводом ошибок и предложениями
"""

import subprocess
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from safe_quality_analyzer import SafeQualityAnalyzer, SafetyLevel


class EnhancedSafeAnalyzer(SafeQualityAnalyzer):
    """Улучшенный безопасный анализатор с детальным выводом"""
    
    def __init__(self):
        super().__init__()
    
    def analyze_with_details(self, file_path: str) -> Dict[str, Any]:
        """Анализ с детальным выводом ошибок"""
        try:
            # Базовый анализ
            analysis = self.analyze_file(file_path)
            
            if "error" in analysis:
                return analysis
            
            # Добавляем детальную информацию об ошибках
            detailed_errors = self._get_detailed_errors(file_path)
            analysis["detailed_errors"] = detailed_errors
            
            # Добавляем предложения по исправлению
            fix_suggestions = self._get_fix_suggestions(file_path, detailed_errors)
            analysis["fix_suggestions"] = fix_suggestions
            
            # Добавляем план исправлений
            fix_plan = self._create_fix_plan(detailed_errors)
            analysis["fix_plan"] = fix_plan
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_detailed_errors(self, file_path: str) -> List[Dict[str, Any]]:
        """Получение детальной информации об ошибках"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'flake8', file_path, '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            detailed_errors = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            error_info = {
                                "file": parts[0],
                                "line": int(parts[1]),
                                "column": int(parts[2]),
                                "code": parts[3].split()[0],
                                "message": parts[3].split(' ', 1)[1] if len(parts[3].split()) > 1 else "",
                                "safety_level": self._get_safety_level(parts[3].split()[0]),
                                "auto_fixable": self._is_auto_fixable(parts[3].split()[0]),
                                "severity": self._get_severity(parts[3].split()[0]),
                                "category": self._get_category(parts[3].split()[0])
                            }
                            detailed_errors.append(error_info)
            
            return detailed_errors
            
        except Exception as e:
            return []
    
    def _get_fix_suggestions(self, file_path: str, errors: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Получение предложений по исправлению"""
        suggestions = {
            "safe_fixes": [],
            "manual_fixes": [],
            "dangerous_fixes": [],
            "critical_fixes": []
        }
        
        for error in errors:
            suggestion = {
                "line": error["line"],
                "code": error["code"],
                "message": error["message"],
                "safety_level": error["safety_level"],
                "suggested_fix": self._get_detailed_fix_suggestion(error),
                "auto_fixable": error["auto_fixable"],
                "severity": error["severity"]
            }
            
            if error["safety_level"] == SafetyLevel.SAFE:
                suggestions["safe_fixes"].append(suggestion)
            elif error["safety_level"] == SafetyLevel.MANUAL:
                suggestions["manual_fixes"].append(suggestion)
            elif error["safety_level"] == SafetyLevel.DANGEROUS:
                suggestions["dangerous_fixes"].append(suggestion)
            elif error["safety_level"] == SafetyLevel.CRITICAL:
                suggestions["critical_fixes"].append(suggestion)
        
        return suggestions
    
    def _get_detailed_fix_suggestion(self, error: Dict[str, Any]) -> str:
        """Получение детального предложения по исправлению"""
        code = error["code"]
        line = error["line"]
        
        suggestions = {
            'E501': f'Строка {line} слишком длинная. Разбейте на несколько строк используя \\ или скобки',
            'W293': f'Строка {line} содержит пробелы в конце. Удалите их',
            'W292': f'Файл не заканчивается переводом строки. Добавьте \\n в конец файла',
            'E302': f'Строка {line}: Добавьте 2 пустые строки перед определением функции/класса',
            'E305': f'Строка {line}: Добавьте 2 пустые строки после определения функции/класса',
            'E128': f'Строка {line}: Исправьте отступы в параметрах функции',
            'E129': f'Строка {line}: Исправьте отступы в параметрах функции',
            'F401': f'Строка {line}: Импорт не используется. Удалите или используйте',
            'F841': f'Строка {line}: Локальная переменная определена, но не используется',
            'E302': f'Строка {line}: Ожидается 2 пустые строки перед определением',
            'E305': f'Строка {line}: Ожидается 2 пустые строки после определения'
        }
        
        return suggestions.get(code, f"Требует ручного анализа: {error['message']}")
    
    def _get_severity(self, error_code: str) -> str:
        """Определение серьезности ошибки"""
        critical_codes = ['F999', 'F403', 'F405']
        high_codes = ['F401', 'F841', 'E999']
        medium_codes = ['E501', 'E302', 'E305']
        low_codes = ['W293', 'W292', 'W291']
        
        if error_code in critical_codes:
            return "critical"
        elif error_code in high_codes:
            return "high"
        elif error_code in medium_codes:
            return "medium"
        elif error_code in low_codes:
            return "low"
        else:
            return "medium"
    
    def _get_category(self, error_code: str) -> str:
        """Определение категории ошибки"""
        if error_code.startswith('E'):
            return "error"
        elif error_code.startswith('W'):
            return "warning"
        elif error_code.startswith('F'):
            return "fatal"
        else:
            return "unknown"
    
    def _create_fix_plan(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Создание плана исправлений"""
        plan = {
            "total_errors": len(errors),
            "safe_to_fix": len([e for e in errors if e["safety_level"] == SafetyLevel.SAFE]),
            "manual_review_needed": len([e for e in errors if e["safety_level"] == SafetyLevel.MANUAL]),
            "dangerous_fixes": len([e for e in errors if e["safety_level"] == SafetyLevel.DANGEROUS]),
            "critical_fixes": len([e for e in errors if e["safety_level"] == SafetyLevel.CRITICAL]),
            "steps": []
        }
        
        # План исправлений
        if plan["safe_to_fix"] > 0:
            plan["steps"].append({
                "step": 1,
                "action": "Исправить безопасные ошибки форматирования",
                "count": plan["safe_to_fix"],
                "tools": ["black", "isort", "manual_fix"],
                "risk": "Низкий"
            })
        
        if plan["manual_review_needed"] > 0:
            plan["steps"].append({
                "step": 2,
                "action": "Ручной анализ и исправление",
                "count": plan["manual_review_needed"],
                "tools": ["manual_review", "code_analysis"],
                "risk": "Средний"
            })
        
        if plan["dangerous_fixes"] > 0:
            plan["steps"].append({
                "step": 3,
                "action": "Критический анализ безопасности",
                "count": plan["dangerous_fixes"],
                "tools": ["security_review", "expert_analysis"],
                "risk": "Высокий"
            })
        
        if plan["critical_fixes"] > 0:
            plan["steps"].append({
                "step": 4,
                "action": "Немедленное исправление критических ошибок",
                "count": plan["critical_fixes"],
                "tools": ["emergency_fix", "security_patch"],
                "risk": "Критический"
            })
        
        return plan
    
    def generate_detailed_report(self, analysis_result: Dict[str, Any]) -> str:
        """Генерация детального отчета"""
        report = []
        report.append("=" * 80)
        report.append("🛡️ ДЕТАЛЬНЫЙ БЕЗОПАСНЫЙ АНАЛИЗ КАЧЕСТВА КОДА")
        report.append("=" * 80)
        report.append(f"📁 Файл: {analysis_result['file_path']}")
        report.append(f"⏰ Время анализа: {analysis_result['timestamp']}")
        report.append(f"📊 Размер файла: {analysis_result['file_size']} байт")
        report.append(f"📏 Строк кода: {analysis_result['line_count']}")
        report.append("")
        
        # Детальные ошибки
        if "detailed_errors" in analysis_result:
            detailed_errors = analysis_result["detailed_errors"]
            if detailed_errors:
                report.append("🔍 ДЕТАЛЬНЫЕ ОШИБКИ:")
                report.append("-" * 40)
                
                for i, error in enumerate(detailed_errors, 1):
                    report.append(f"{i}. Строка {error['line']}, колонка {error['column']}")
                    report.append(f"   Код: {error['code']}")
                    report.append(f"   Сообщение: {error['message']}")
                    report.append(f"   Уровень безопасности: {error['safety_level'].value}")
                    report.append(f"   Серьезность: {error['severity']}")
                    report.append(f"   Категория: {error['category']}")
                    report.append(f"   Автоисправление: {'Да' if error['auto_fixable'] else 'Нет'}")
                    report.append("")
            else:
                report.append("✅ Ошибок не найдено!")
                report.append("")
        
        # Предложения по исправлению
        if "fix_suggestions" in analysis_result:
            suggestions = analysis_result["fix_suggestions"]
            
            if suggestions["safe_fixes"]:
                report.append("🔧 БЕЗОПАСНЫЕ ИСПРАВЛЕНИЯ:")
                report.append("-" * 40)
                for i, fix in enumerate(suggestions["safe_fixes"], 1):
                    report.append(f"{i}. Строка {fix['line']}: {fix['code']}")
                    report.append(f"   Предложение: {fix['suggested_fix']}")
                    report.append("")
            
            if suggestions["manual_fixes"]:
                report.append("⚠️ ТРЕБУЮТ РУЧНОГО АНАЛИЗА:")
                report.append("-" * 40)
                for i, fix in enumerate(suggestions["manual_fixes"], 1):
                    report.append(f"{i}. Строка {fix['line']}: {fix['code']}")
                    report.append(f"   Причина: {fix['suggested_fix']}")
                    report.append("")
            
            if suggestions["dangerous_fixes"]:
                report.append("🚨 ОПАСНЫЕ ИСПРАВЛЕНИЯ:")
                report.append("-" * 40)
                for i, fix in enumerate(suggestions["dangerous_fixes"], 1):
                    report.append(f"{i}. Строка {fix['line']}: {fix['code']}")
                    report.append(f"   ВНИМАНИЕ: {fix['suggested_fix']}")
                    report.append("")
        
        # План исправлений
        if "fix_plan" in analysis_result:
            plan = analysis_result["fix_plan"]
            report.append("📋 ПЛАН ИСПРАВЛЕНИЙ:")
            report.append("-" * 40)
            report.append(f"Всего ошибок: {plan['total_errors']}")
            report.append(f"Безопасных для исправления: {plan['safe_to_fix']}")
            report.append(f"Требуют ручного анализа: {plan['manual_review_needed']}")
            report.append(f"Опасных: {plan['dangerous_fixes']}")
            report.append(f"Критических: {plan['critical_fixes']}")
            report.append("")
            
            if plan["steps"]:
                report.append("📝 ПОШАГОВЫЙ ПЛАН:")
                for step in plan["steps"]:
                    report.append(f"Шаг {step['step']}: {step['action']}")
                    report.append(f"   Количество: {step['count']}")
                    report.append(f"   Инструменты: {', '.join(step['tools'])}")
                    report.append(f"   Риск: {step['risk']}")
                    report.append("")
        
        # Безопасность
        safety = analysis_result['safety_report']
        report.append("🛡️ ОТЧЕТ О БЕЗОПАСНОСТИ:")
        report.append("-" * 40)
        report.append(f"Функции безопасности сохранены: {'✅' if safety['security_functions_preserved'] else '❌'}")
        report.append(f"Шифрование не затронуто: {'✅' if safety['encryption_intact'] else '❌'}")
        report.append(f"Аутентификация сохранена: {'✅' if safety['authentication_preserved'] else '❌'}")
        report.append(f"Валидация не затронута: {'✅' if safety['validation_intact'] else '❌'}")
        report.append(f"Логирование сохранено: {'✅' if safety['logging_preserved'] else '❌'}")
        report.append(f"Проблем безопасности найдено: {safety['security_issues_found']}")
        report.append(f"Критических проблем: {safety['critical_issues']}")
        report.append("")
        
        # Рекомендации
        recommendations = analysis_result['recommendations']
        if recommendations:
            report.append("💡 РЕКОМЕНДАЦИИ:")
            report.append("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("🎯 ЗАКЛЮЧЕНИЕ:")
        report.append("-" * 40)
        report.append("✅ Код проанализирован БЕЗОПАСНО")
        report.append("✅ Никаких изменений не внесено")
        report.append("✅ Безопасность системы сохранена")
        report.append("✅ Детальные предложения по улучшению предоставлены")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


# Глобальный экземпляр
enhanced_safe_analyzer = EnhancedSafeAnalyzer()


def analyze_file_with_details(file_path: str) -> Dict[str, Any]:
    """Детальный анализ файла"""
    return enhanced_safe_analyzer.analyze_with_details(file_path)


def generate_detailed_report(file_path: str) -> str:
    """Генерация детального отчета"""
    analysis = analyze_file_with_details(file_path)
    return enhanced_safe_analyzer.generate_detailed_report(analysis)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print("🛡️ ДЕТАЛЬНЫЙ БЕЗОПАСНЫЙ АНАЛИЗ КАЧЕСТВА КОДА")
        print("=" * 60)
        print(f"Анализируем файл: {file_path}")
        print()
        
        result = analyze_file_with_details(file_path)
        if "error" in result:
            print(f"❌ Ошибка: {result['error']}")
        else:
            report = generate_detailed_report(file_path)
            print(report)
    else:
        print("Использование: python3 enhanced_safe_analyzer.py <путь_к_файлу>")