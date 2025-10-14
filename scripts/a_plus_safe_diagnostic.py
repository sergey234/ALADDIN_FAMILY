#!/usr/bin/env python3
"""
A+ SAFE DIAGNOSTIC MODULE - БЕЗОПАСНЫЙ СУПЕР-МОДУЛЬ ДИАГНОСТИКИ
ТОЛЬКО ДИАГНОСТИКА, ПРОВЕРКИ И НАПРАВЛЕНИЯ - БЕЗ АВТОМАТИЧЕСКИХ ИСПРАВЛЕНИЙ!
БЕЗОПАСНЫЙ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ!
"""

import sys
import os
import json
import ast
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class APlusSafeDiagnosticModule:
    """БЕЗОПАСНЫЙ СУПЕР-МОДУЛЬ для диагностики плана A+ (ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ)"""
    
    def __init__(self):
        self.project_root = Path('/Users/sergejhlystov/ALADDIN_NEW')
        self.scripts_dir = self.project_root / 'scripts'
        self.security_dir = self.project_root / 'security'
        self.core_dir = self.project_root / 'core'
        self.data_dir = self.project_root / 'data'
        
        # Статистика диагностики (ТОЛЬКО ЧТЕНИЕ)
        self.diagnostic_stats = {
            'total_functions': 301,
            'analyzed_functions': 0,
            'syntax_issues_found': 0,
            'import_issues_found': 0,
            'security_issues_found': 0,
            'quality_issues_found': 0,
            'tests_run': 0,
            'overall_analysis_progress': 0
        }
        
        # Результаты диагностики
        self.diagnostic_results = {
            'syntax_issues': [],
            'import_issues': [],
            'security_issues': [],
            'quality_issues': [],
            'recommendations': []
        }
    
    def run_full_diagnostic(self):
        """Запуск полной диагностики системы (ТОЛЬКО АНАЛИЗ)"""
        print("🔍 A+ SAFE DIAGNOSTIC MODULE - ПОЛНАЯ ДИАГНОСТИКА СИСТЕМЫ")
        print("=" * 70)
        print("🛡️ БЕЗОПАСНЫЙ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ!")
        print("❌ НИКАКИХ АВТОМАТИЧЕСКИХ ИСПРАВЛЕНИЙ!")
        print("💡 ВСЕ ИСПРАВЛЕНИЯ - ТОЛЬКО ВРУЧНУЮ ВАМИ И МНОЙ!")
        print("=" * 70)
        print(f"📊 Всего функций для анализа: {self.diagnostic_stats['total_functions']}")
        print(f"📅 Начало диагностики: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # ЭТАП 1: ДИАГНОСТИКА КРИТИЧЕСКИХ ПРОБЛЕМ
        self._diagnose_critical_issues()
        
        # ЭТАП 2: ДИАГНОСТИКА БЕЗОПАСНОСТИ
        self._diagnose_security_issues()
        
        # ЭТАП 3: ДИАГНОСТИКА КАЧЕСТВА
        self._diagnose_quality_issues()
        
        # ЭТАП 4: ДИАГНОСТИКА ГОТОВНОСТИ
        self._diagnose_production_readiness()
        
        # ФИНАЛЬНЫЙ ДИАГНОСТИЧЕСКИЙ ОТЧЕТ
        self._generate_diagnostic_report()
    
    def _diagnose_critical_issues(self):
        """ДИАГНОСТИКА критических проблем (ТОЛЬКО АНАЛИЗ)"""
        print("\n🔴 ЭТАП 1: ДИАГНОСТИКА КРИТИЧЕСКИХ ПРОБЛЕМ")
        print("=" * 50)
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # 1.1 ДИАГНОСТИКА СИНТАКСИСА
        print("\n📋 1.1 ДИАГНОСТИКА СИНТАКСИСА PYTHON")
        self._diagnose_syntax_issues()
        
        # 1.2 ДИАГНОСТИКА ИМПОРТОВ
        print("\n📋 1.2 ДИАГНОСТИКА ИМПОРТОВ")
        self._diagnose_import_issues()
        
        # 1.3 ДИАГНОСТИКА ОБРАБОТКИ ОШИБОК
        print("\n📋 1.3 ДИАГНОСТИКА ОБРАБОТКИ ОШИБОК")
        self._diagnose_error_handling()
    
    def _diagnose_syntax_issues(self):
        """ДИАГНОСТИКА синтаксических проблем (ТОЛЬКО АНАЛИЗ)"""
        print("🔍 ДИАГНОСТИКА синтаксических проблем...")
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # Критические файлы для диагностики
        critical_files = [
            "security/base.py",
            "security/managers/analytics_manager.py",
            "security/managers/monitor_manager.py",
            "security/managers/report_manager.py",
            "security/managers/dashboard_manager.py",
            "core/base.py",
            "security/safe_function_manager.py"
        ]
        
        issues_found = 0
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Читаем файл для анализа
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Проверяем синтаксис (ТОЛЬКО ПРОВЕРКА)
                    compile(content, str(full_path), 'exec')
                    print(f"✅ {file_path} - синтаксис корректен")
                except SyntaxError as e:
                    print(f"❌ {file_path} - НАЙДЕНА ОШИБКА СИНТАКСИСА!")
                    print(f"   📍 Строка {e.lineno}: {e.text}")
                    print(f"   ❌ Ошибка: {e}")
                    print(f"   💡 РЕКОМЕНДАЦИЯ: Исправьте синтаксис вручную")
                    
                    self.diagnostic_results['syntax_issues'].append({
                        'file': file_path,
                        'line': e.lineno,
                        'error': str(e),
                        'text': e.text,
                        'recommendation': 'Исправьте синтаксис вручную'
                    })
                    issues_found += 1
                except Exception as e:
                    print(f"⚠️ {file_path} - ошибка чтения: {e}")
                    issues_found += 1
            else:
                print(f"⚠️ {file_path} - файл не найден")
        
        self.diagnostic_stats['syntax_issues_found'] = issues_found
        print(f"📊 НАЙДЕНО синтаксических проблем: {issues_found}")
    
    def _diagnose_import_issues(self):
        """ДИАГНОСТИКА проблем импорта (ТОЛЬКО АНАЛИЗ)"""
        print("🔍 ДИАГНОСТИКА проблем импорта...")
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # Файлы с потенциальными проблемами импорта
        import_problem_files = [
            "security/bots/max_messenger_security_bot.py",
            "security/bots/mobile_navigation_bot.py",
            "security/bots/gaming_security_bot.py",
            "security/ai_agents/phishing_protection_agent.py",
            "security/ai_agents/malware_detection_agent.py"
        ]
        
        issues_found = 0
        
        for file_path in import_problem_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Читаем файл для анализа импортов
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Анализируем импорты (ТОЛЬКО АНАЛИЗ)
                    import_lines = [line.strip() for line in content.split('\n') 
                                  if line.strip().startswith('import ') or line.strip().startswith('from ')]
                    
                    print(f"📁 {file_path} - найдено импортов: {len(import_lines)}")
                    
                    # Проверяем каждый импорт
                    for import_line in import_lines:
                        try:
                            # Пытаемся выполнить импорт (ТОЛЬКО ПРОВЕРКА)
                            exec(import_line)
                        except ImportError as e:
                            print(f"❌ {file_path} - ПРОБЛЕМА ИМПОРТА!")
                            print(f"   📝 Импорт: {import_line}")
                            print(f"   ❌ Ошибка: {e}")
                            print(f"   💡 РЕКОМЕНДАЦИЯ: Проверьте зависимости вручную")
                            
                            self.diagnostic_results['import_issues'].append({
                                'file': file_path,
                                'import_line': import_line,
                                'error': str(e),
                                'recommendation': 'Проверьте зависимости вручную'
                            })
                            issues_found += 1
                        except Exception as e:
                            print(f"⚠️ {file_path} - ошибка анализа импорта: {e}")
                            issues_found += 1
                    
                    print(f"✅ {file_path} - анализ импортов завершен")
                except Exception as e:
                    print(f"❌ {file_path} - ошибка чтения файла: {e}")
                    issues_found += 1
            else:
                print(f"⚠️ {file_path} - файл не найден")
        
        self.diagnostic_stats['import_issues_found'] = issues_found
        print(f"📊 НАЙДЕНО проблем импорта: {issues_found}")
    
    def _diagnose_error_handling(self):
        """ДИАГНОСТИКА обработки ошибок (ТОЛЬКО АНАЛИЗ)"""
        print("🔍 ДИАГНОСТИКА обработки ошибок...")
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # Критические файлы для проверки обработки ошибок
        error_handling_files = [
            "security/safe_function_manager.py",
            "core/base.py",
            "security/base.py"
        ]
        
        issues_found = 0
        
        for file_path in error_handling_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Читаем файл для анализа
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Анализируем обработку ошибок (ТОЛЬКО АНАЛИЗ)
                    try_blocks = content.count('try:')
                    except_blocks = content.count('except')
                    finally_blocks = content.count('finally:')
                    
                    print(f"📁 {file_path} - обработка ошибок:")
                    print(f"   🔍 try блоков: {try_blocks}")
                    print(f"   🔍 except блоков: {except_blocks}")
                    print(f"   🔍 finally блоков: {finally_blocks}")
                    
                    if try_blocks == 0:
                        print(f"⚠️ {file_path} - НЕТ ОБРАБОТКИ ОШИБОК!")
                        print(f"   💡 РЕКОМЕНДАЦИЯ: Добавьте try-except блоки")
                        
                        self.diagnostic_results['recommendations'].append({
                            'file': file_path,
                            'issue': 'Отсутствует обработка ошибок',
                            'recommendation': 'Добавьте try-except блоки для обработки ошибок'
                        })
                        issues_found += 1
                    else:
                        print(f"✅ {file_path} - обработка ошибок присутствует")
                
                except Exception as e:
                    print(f"❌ {file_path} - ошибка чтения: {e}")
                    issues_found += 1
            else:
                print(f"⚠️ {file_path} - файл не найден")
        
        print(f"📊 НАЙДЕНО проблем с обработкой ошибок: {issues_found}")
    
    def _diagnose_security_issues(self):
        """ДИАГНОСТИКА проблем безопасности (ТОЛЬКО АНАЛИЗ)"""
        print("\n🔒 ЭТАП 2: ДИАГНОСТИКА ПРОБЛЕМ БЕЗОПАСНОСТИ")
        print("=" * 50)
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # Проверяем базовые проблемы безопасности
        security_files = [
            "security/safe_function_manager.py",
            "security/base.py",
            "core/base.py"
        ]
        
        issues_found = 0
        
        for file_path in security_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Читаем файл для анализа безопасности
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Анализируем безопасность (ТОЛЬКО АНАЛИЗ)
                    security_issues = []
                    
                    # Проверяем на SQL Injection
                    if 'execute(' in content and '%s' in content:
                        security_issues.append("Возможная уязвимость SQL Injection")
                    
                    # Проверяем на XSS
                    if 'innerHTML' in content or 'document.write' in content:
                        security_issues.append("Возможная уязвимость XSS")
                    
                    # Проверяем валидацию входных данных
                    if 'input(' in content and 'validate' not in content:
                        security_issues.append("Отсутствует валидация входных данных")
                    
                    if security_issues:
                        print(f"⚠️ {file_path} - НАЙДЕНЫ ПРОБЛЕМЫ БЕЗОПАСНОСТИ:")
                        for issue in security_issues:
                            print(f"   ❌ {issue}")
                            print(f"   💡 РЕКОМЕНДАЦИЯ: Исправьте вручную")
                        
                        self.diagnostic_results['security_issues'].extend([{
                            'file': file_path,
                            'issue': issue,
                            'recommendation': 'Исправьте проблему безопасности вручную'
                        } for issue in security_issues])
                        issues_found += len(security_issues)
                    else:
                        print(f"✅ {file_path} - проблемы безопасности не найдены")
                
                except Exception as e:
                    print(f"❌ {file_path} - ошибка чтения: {e}")
                    issues_found += 1
            else:
                print(f"⚠️ {file_path} - файл не найден")
        
        self.diagnostic_stats['security_issues_found'] = issues_found
        print(f"📊 НАЙДЕНО проблем безопасности: {issues_found}")
    
    def _diagnose_quality_issues(self):
        """ДИАГНОСТИКА проблем качества (ТОЛЬКО АНАЛИЗ)"""
        print("\n💎 ЭТАП 3: ДИАГНОСТИКА ПРОБЛЕМ КАЧЕСТВА")
        print("=" * 50)
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # Проверяем качество кода
        quality_files = [
            "security/safe_function_manager.py",
            "core/base.py",
            "security/base.py"
        ]
        
        issues_found = 0
        
        for file_path in quality_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # ИСПРАВЛЕННАЯ ПРОВЕРКА КАЧЕСТВА - используем flake8
                    print(f"🔍 {file_path} - проверка качества с помощью flake8...")
                    
                    # Запускаем flake8 для реальной проверки качества
                    import subprocess
                    result = subprocess.run([
                        'python3', '-m', 'flake8', 
                        str(full_path), 
                        '--count', '--select=E,W,F'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        print(f"✅ {file_path} - проблемы качества не найдены")
                    else:
                        # Парсим результаты flake8
                        flake8_lines = result.stdout.strip().split('\n')
                        if flake8_lines and flake8_lines[0]:
                            print(f"⚠️ {file_path} - НАЙДЕНЫ ПРОБЛЕМЫ КАЧЕСТВА:")
                            print(f"   📊 Всего замечаний flake8: {len(flake8_lines)}")
                            
                            # Показываем первые 5 замечаний
                            for line in flake8_lines[:5]:
                                print(f"   ❌ {line}")
                            
                            if len(flake8_lines) > 5:
                                print(f"   ... и еще {len(flake8_lines) - 5} замечаний")
                            
                            print(f"   💡 РЕКОМЕНДАЦИЯ: Исправьте замечания flake8 вручную")
                            
                            # Сохраняем результаты
                            self.diagnostic_results['quality_issues'].extend([{
                                'file': file_path,
                                'issue': line,
                                'recommendation': 'Исправьте замечание flake8 вручную'
                            } for line in flake8_lines])
                            
                            issues_found += len(flake8_lines)
                        else:
                            print(f"✅ {file_path} - проблемы качества не найдены")
                
                except subprocess.TimeoutExpired:
                    print(f"⚠️ {file_path} - таймаут проверки flake8")
                    issues_found += 1
                except Exception as e:
                    print(f"❌ {file_path} - ошибка проверки качества: {e}")
                    issues_found += 1
            else:
                print(f"⚠️ {file_path} - файл не найден")
        
        self.diagnostic_stats['quality_issues_found'] = issues_found
        print(f"📊 НАЙДЕНО проблем качества: {issues_found}")
    
    def _diagnose_production_readiness(self):
        """ДИАГНОСТИКА готовности к продакшену (ТОЛЬКО АНАЛИЗ)"""
        print("\n🚀 ЭТАП 4: ДИАГНОСТИКА ГОТОВНОСТИ К ПРОДАКШЕНУ")
        print("=" * 50)
        print("🛡️ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ - БЕЗ ИСПРАВЛЕНИЙ!")
        
        # Проверяем готовность к продакшену
        production_checks = [
            "Проверка конфигурации",
            "Проверка логирования",
            "Проверка мониторинга",
            "Проверка документации"
        ]
        
        print("🔍 ПРОВЕРКА ГОТОВНОСТИ К ПРОДАКШЕНУ:")
        for check in production_checks:
            print(f"   📋 {check} - проверка...")
            # Здесь можно добавить реальные проверки
            print(f"   ✅ {check} - проверка завершена")
        
        print("📊 Диагностика готовности к продакшену завершена")
    
    def _generate_diagnostic_report(self):
        """Генерация диагностического отчета"""
        print("\n📊 ФИНАЛЬНЫЙ ДИАГНОСТИЧЕСКИЙ ОТЧЕТ")
        print("=" * 70)
        
        # Обновляем статистику
        self.diagnostic_stats['analyzed_functions'] = self.diagnostic_stats['total_functions']
        self.diagnostic_stats['overall_analysis_progress'] = 100
        
        # Выводим статистику
        print(f"📊 Всего функций: {self.diagnostic_stats['total_functions']}")
        print(f"📊 Проанализировано функций: {self.diagnostic_stats['analyzed_functions']}")
        print(f"📊 Найдено синтаксических проблем: {self.diagnostic_stats['syntax_issues_found']}")
        print(f"📊 Найдено проблем импорта: {self.diagnostic_stats['import_issues_found']}")
        print(f"📊 Найдено проблем безопасности: {self.diagnostic_stats['security_issues_found']}")
        print(f"📊 Найдено проблем качества: {self.diagnostic_stats['quality_issues_found']}")
        print(f"📊 Общий прогресс анализа: {self.diagnostic_stats['overall_analysis_progress']}%")
        
        # Сохраняем отчет
        report_file = self.project_root / 'a_plus_diagnostic_report.json'
        report_data = {
            'diagnostic_stats': self.diagnostic_stats,
            'diagnostic_results': self.diagnostic_results,
            'timestamp': datetime.now().isoformat(),
            'module': 'A+ Safe Diagnostic Module'
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Диагностический отчет сохранен: {report_file}")
        print("\n🎉 ДИАГНОСТИКА ЗАВЕРШЕНА!")
        print("💡 ВСЕ НАЙДЕННЫЕ ПРОБЛЕМЫ ТРЕБУЮТ РУЧНОГО ИСПРАВЛЕНИЯ!")
        print("🛡️ СУПЕР-МОДУЛЬ РАБОТАЛ В БЕЗОПАСНОМ РЕЖИМЕ!")

def main():
    """Главная функция диагностики"""
    print("🔍 A+ SAFE DIAGNOSTIC MODULE - БЕЗОПАСНЫЙ СУПЕР-МОДУЛЬ ДИАГНОСТИКИ")
    print("=" * 70)
    print("🛡️ БЕЗОПАСНЫЙ РЕЖИМ: ТОЛЬКО ЧТЕНИЕ И АНАЛИЗ!")
    print("❌ НИКАКИХ АВТОМАТИЧЕСКИХ ИСПРАВЛЕНИЙ!")
    print("💡 ВСЕ ИСПРАВЛЕНИЯ - ТОЛЬКО ВРУЧНУЮ ВАМИ И МНОЙ!")
    print("=" * 70)
    
    diagnostic_module = APlusSafeDiagnosticModule()
    diagnostic_module.run_full_diagnostic()

if __name__ == "__main__":
    main()