#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный анализ качества кода всех функций в SafeFunctionManager
Проверка: PEP8, SOLID, DRY, Безопасность, Архитектура
"""

import os
import sys
import ast
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Добавляем путь к модулям
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class CodeQualityAnalyzer:
    """Анализатор качества кода"""
    
    def __init__(self):
        self.base_path = "/Users/sergejhlystov/ALADDIN_NEW"
        self.issues = []
        self.function_analysis = {}
        self.overall_score = 0
        
    def analyze_file(self, file_path):
        """Анализ одного файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг AST
            tree = ast.parse(content)
            
            file_analysis = {
                'file_path': file_path,
                'pep8_issues': [],
                'solid_issues': [],
                'dry_issues': [],
                'security_issues': [],
                'architecture_issues': [],
                'docstring_issues': [],
                'complexity_issues': [],
                'readability_issues': [],
                'score': 0
            }
            
            # Анализ PEP8
            self._analyze_pep8(content, file_analysis)
            
            # Анализ SOLID принципов
            self._analyze_solid(tree, file_analysis)
            
            # Анализ DRY принципа
            self._analyze_dry(content, file_analysis)
            
            # Анализ безопасности
            self._analyze_security(content, file_analysis)
            
            # Анализ архитектуры
            self._analyze_architecture(tree, file_analysis)
            
            # Анализ docstrings
            self._analyze_docstrings(tree, file_analysis)
            
            # Анализ сложности
            self._analyze_complexity(tree, file_analysis)
            
            # Анализ читаемости
            self._analyze_readability(content, file_analysis)
            
            # Подсчет общего балла
            self._calculate_score(file_analysis)
            
            return file_analysis
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'score': 0
            }
    
    def _analyze_pep8(self, content, analysis):
        """Анализ PEP8 нарушений"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Проверка длины строки
            if len(line) > 120:
                analysis['pep8_issues'].append(f"Line {i}: Line too long ({len(line)} > 120)")
            
            # Проверка отступов
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if i > 1 and lines[i-2].strip().endswith(':'):
                    if not line.startswith('    '):
                        analysis['pep8_issues'].append(f"Line {i}: Expected 4 spaces for indentation")
            
            # Проверка пробелов
            if line.strip().endswith(' '):
                analysis['pep8_issues'].append(f"Line {i}: Trailing whitespace")
            
            if '  ' in line and not line.strip().startswith('#'):
                analysis['pep8_issues'].append(f"Line {i}: Multiple spaces")
    
    def _analyze_solid(self, tree, analysis):
        """Анализ SOLID принципов"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Single Responsibility Principle
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 10:
                    analysis['solid_issues'].append(f"Class {node.name}: Too many methods ({len(methods)}) - SRP violation")
                
                # Interface Segregation Principle
                abstract_methods = [n for n in methods if any(isinstance(d, ast.Name) and d.id == 'abstractmethod' for d in n.decorator_list)]
                if len(abstract_methods) > 5:
                    analysis['solid_issues'].append(f"Class {node.name}: Too many abstract methods ({len(abstract_methods)}) - ISP violation")
            
            elif isinstance(node, ast.FunctionDef):
                # Open/Closed Principle - проверка на жестко закодированные значения
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        if len(child.value) > 50 and not child.value.startswith('http'):
                            analysis['solid_issues'].append(f"Function {node.name}: Hardcoded string - OCP violation")
    
    def _analyze_dry(self, content, analysis):
        """Анализ DRY принципа"""
        lines = content.split('\n')
        
        # Поиск дублированных блоков кода
        code_blocks = {}
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line in code_blocks:
                    code_blocks[line].append(i + 1)
                else:
                    code_blocks[line] = [i + 1]
        
        for line, occurrences in code_blocks.items():
            if len(occurrences) > 3:
                analysis['dry_issues'].append(f"Duplicate code block: '{line[:50]}...' appears {len(occurrences)} times at lines {occurrences}")
    
    def _analyze_security(self, content, analysis):
        """Анализ безопасности"""
        security_patterns = {
            'sql_injection': [r'execute\s*\(\s*["\'].*%.*["\']', r'cursor\.execute\s*\(\s*f["\']'],
            'xss': [r'innerHTML\s*=', r'document\.write\s*\('],
            'unsafe_eval': [r'eval\s*\(', r'exec\s*\('],
            'hardcoded_secrets': [r'password\s*=\s*["\'][^"\']+["\']', r'secret\s*=\s*["\'][^"\']+["\']'],
            'weak_crypto': [r'md5\s*\(', r'sha1\s*\('],
            'path_traversal': [r'open\s*\(\s*[^)]*\+', r'file\s*\(\s*[^)]*\+']
        }
        
        for pattern_name, patterns in security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    analysis['security_issues'].append(f"Line {line_num}: Potential {pattern_name} vulnerability")
    
    def _analyze_architecture(self, tree, analysis):
        """Анализ архитектуры"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Проверка на God Class
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:
                    analysis['architecture_issues'].append(f"Class {node.name}: God Class detected ({len(methods)} methods)")
                
                # Проверка на Feature Envy
                for method in methods:
                    external_calls = 0
                    for child in ast.walk(method):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                            if not child.func.value.id == 'self':
                                external_calls += 1
                    
                    if external_calls > 5:
                        analysis['architecture_issues'].append(f"Method {method.name}: Feature Envy detected ({external_calls} external calls)")
    
    def _analyze_docstrings(self, tree, analysis):
        """Анализ docstrings"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    analysis['docstring_issues'].append(f"{type(node).__name__} {node.name}: Missing docstring")
                else:
                    docstring = ast.get_docstring(node)
                    if len(docstring) < 20:
                        analysis['docstring_issues'].append(f"{type(node).__name__} {node.name}: Docstring too short")
    
    def _analyze_complexity(self, tree, analysis):
        """Анализ цикломатической сложности"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = 1  # Базовая сложность
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                
                if complexity > 10:
                    analysis['complexity_issues'].append(f"Function {node.name}: High cyclomatic complexity ({complexity})")
    
    def _analyze_readability(self, content, analysis):
        """Анализ читаемости"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Проверка на слишком длинные имена переменных
            words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line)
            for word in words:
                if len(word) > 30:
                    analysis['readability_issues'].append(f"Line {i}: Variable name too long: {word}")
            
            # Проверка на слишком короткие имена
            for word in words:
                if len(word) == 1 and word.isalpha() and word not in ['i', 'j', 'k', 'x', 'y', 'z']:
                    analysis['readability_issues'].append(f"Line {i}: Variable name too short: {word}")
            
            # Проверка на магические числа
            numbers = re.findall(r'\b\d+\b', line)
            for num in numbers:
                if int(num) > 100 and not line.strip().startswith('#'):
                    analysis['readability_issues'].append(f"Line {i}: Magic number: {num}")
    
    def _calculate_score(self, analysis):
        """Подсчет общего балла качества"""
        total_issues = (
            len(analysis['pep8_issues']) +
            len(analysis['solid_issues']) +
            len(analysis['dry_issues']) +
            len(analysis['security_issues']) +
            len(analysis['architecture_issues']) +
            len(analysis['docstring_issues']) +
            len(analysis['complexity_issues']) +
            len(analysis['readability_issues'])
        )
        
        # Базовый балл 100, вычитаем за каждую проблему
        analysis['score'] = max(0, 100 - total_issues * 2)
    
    def analyze_all_functions(self):
        """Анализ всех функций в системе"""
        print("🔍 КОМПЛЕКСНЫЙ АНАЛИЗ КАЧЕСТВА КОДА")
        print("=" * 80)
        print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Список всех файлов для анализа
        files_to_analyze = [
            # Core файлы
            "core/base.py",
            "core/service_base.py",
            "core/database.py",
            "core/configuration.py",
            "core/logging_module.py",
            "core/security_base.py",
            
            # Security основные файлы
            "security/safe_function_manager.py",
            "security/security_monitoring.py",
            "security/authentication.py",
            "security/access_control.py",
            "security/security_policy.py",
            "security/security_reporting.py",
            
            # Family функции
            "security/family/family_profile_manager.py",
            "security/family/child_protection.py",
            "security/family/elderly_protection.py",
            
            # Preliminary функции
            "security/preliminary/policy_engine.py",
            "security/preliminary/risk_assessment.py",
            "security/preliminary/behavioral_analysis.py",
            "security/preliminary/mfa_service.py",
            "security/preliminary/zero_trust_service.py",
            "security/preliminary/trust_scoring.py",
            "security/preliminary/context_aware_access.py",
            
            # Reactive функции
            "security/reactive/recovery_service.py",
            "security/reactive/threat_intelligence.py",
            "security/reactive/forensics_service.py",
            
            # Microservices
            "security/microservices/api_gateway.py",
            "security/microservices/load_balancer.py",
            "security/microservices/rate_limiter.py",
            "security/microservices/circuit_breaker.py",
            "security/microservices/user_interface_manager.py",
            "security/microservices/redis_cache_manager.py",
            "security/microservices/service_mesh_manager.py",
            
            # AI Agents
            "security/managers/monitor_manager.py",
            "security/managers/alert_manager.py",
            "security/managers/report_manager.py",
            "security/managers/analytics_manager.py",
            "security/managers/dashboard_manager.py",
            "security/ai_agents/data_protection_agent.py",
            "security/ai_agents/mobile_security_agent.py",
            
            # Bots
            "security/bots/mobile_navigation_bot.py",
            "security/bots/gaming_security_bot.py",
            "security/bots/emergency_response_bot.py",
            "security/bots/parental_control_bot.py",
            "security/bots/notification_bot.py",
            "security/bots/whatsapp_security_bot.py",
            "security/bots/telegram_security_bot.py",
            "security/bots/instagram_security_bot.py",
            "security/bots/analytics_bot.py",
            "security/bots/website_navigation_bot.py",
            "security/bots/browser_security_bot.py",
            "security/bots/cloud_storage_security_bot.py",
            "security/bots/network_security_bot.py",
            "security/bots/device_security_bot.py",
            
            # Privacy
            "security/privacy/universal_privacy_manager.py",
            
            # Compliance
            "security/compliance/russian_child_protection_manager.py",
            "security/compliance/russian_data_protection_manager.py",
            
            # CI/CD
            "security/ci_cd/ci_pipeline_manager.py",
            
            # Scaling
            "security/scaling/auto_scaling_engine.py",
            
            # Orchestration
            "security/orchestration/kubernetes_orchestrator.py"
        ]
        
        total_files = len(files_to_analyze)
        analyzed_files = 0
        total_score = 0
        
        print(f"📊 Анализируем {total_files} файлов...")
        print()
        
        for file_path in files_to_analyze:
            full_path = os.path.join(self.base_path, file_path)
            if os.path.exists(full_path):
                print(f"🔍 Анализируем: {file_path}")
                analysis = self.analyze_file(full_path)
                self.function_analysis[file_path] = analysis
                
                if 'error' not in analysis:
                    total_score += analysis['score']
                    analyzed_files += 1
                    
                    # Показываем основные проблемы
                    if analysis['score'] < 80:
                        print(f"   ⚠️  Качество: {analysis['score']}/100")
                        if analysis['pep8_issues']:
                            print(f"   📝 PEP8: {len(analysis['pep8_issues'])} проблем")
                        if analysis['security_issues']:
                            print(f"   🔒 Безопасность: {len(analysis['security_issues'])} проблем")
                        if analysis['solid_issues']:
                            print(f"   🏗️  SOLID: {len(analysis['solid_issues'])} проблем")
                    else:
                        print(f"   ✅ Качество: {analysis['score']}/100")
                else:
                    print(f"   ❌ Ошибка: {analysis['error']}")
            else:
                print(f"❌ Файл не найден: {file_path}")
        
        print()
        print("📊 ОБЩАЯ СТАТИСТИКА КАЧЕСТВА:")
        print("-" * 80)
        
        if analyzed_files > 0:
            average_score = total_score / analyzed_files
            print(f"📈 Средний балл качества: {average_score:.1f}/100")
            print(f"📁 Проанализировано файлов: {analyzed_files}/{total_files}")
            
            # Группировка по качеству
            excellent = len([f for f in self.function_analysis.values() if f.get('score', 0) >= 90])
            good = len([f for f in self.function_analysis.values() if 80 <= f.get('score', 0) < 90])
            fair = len([f for f in self.function_analysis.values() if 70 <= f.get('score', 0) < 80])
            poor = len([f for f in self.function_analysis.values() if f.get('score', 0) < 70])
            
            print(f"🏆 Отличное качество (90-100): {excellent} файлов")
            print(f"✅ Хорошее качество (80-89): {good} файлов")
            print(f"⚠️  Удовлетворительное (70-79): {fair} файлов")
            print(f"❌ Требует улучшения (<70): {poor} файлов")
            
            # Топ проблем
            self._show_top_issues()
            
            # Рекомендации
            self._show_recommendations(average_score)
        
        print()
        print("=" * 80)
        print("✅ АНАЛИЗ КАЧЕСТВА ЗАВЕРШЕН!")
        print("=" * 80)
    
    def _show_top_issues(self):
        """Показать топ проблем"""
        print()
        print("🔍 ТОП ПРОБЛЕМ ПО КАТЕГОРИЯМ:")
        print("-" * 80)
        
        issue_counts = {
            'PEP8': 0,
            'SOLID': 0,
            'DRY': 0,
            'Безопасность': 0,
            'Архитектура': 0,
            'Docstrings': 0,
            'Сложность': 0,
            'Читаемость': 0
        }
        
        for analysis in self.function_analysis.values():
            if 'error' not in analysis:
                issue_counts['PEP8'] += len(analysis['pep8_issues'])
                issue_counts['SOLID'] += len(analysis['solid_issues'])
                issue_counts['DRY'] += len(analysis['dry_issues'])
                issue_counts['Безопасность'] += len(analysis['security_issues'])
                issue_counts['Архитектура'] += len(analysis['architecture_issues'])
                issue_counts['Docstrings'] += len(analysis['docstring_issues'])
                issue_counts['Сложность'] += len(analysis['complexity_issues'])
                issue_counts['Читаемость'] += len(analysis['readability_issues'])
        
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_issues:
            if count > 0:
                print(f"   {category:15} | {count:3d} проблем")
    
    def _show_recommendations(self, average_score):
        """Показать рекомендации"""
        print()
        print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        print("-" * 80)
        
        if average_score < 70:
            print("🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            print("   1. Немедленно исправить все проблемы безопасности")
            print("   2. Добавить docstrings для всех функций и классов")
            print("   3. Исправить PEP8 нарушения")
            print("   4. Рефакторинг сложных функций")
        elif average_score < 80:
            print("⚠️  СРЕДНИЕ ПРОБЛЕМЫ:")
            print("   1. Улучшить архитектуру согласно SOLID принципам")
            print("   2. Устранить дублирование кода (DRY)")
            print("   3. Добавить недостающие docstrings")
            print("   4. Оптимизировать читаемость кода")
        elif average_score < 90:
            print("✅ ХОРОШЕЕ КАЧЕСТВО:")
            print("   1. Мелкие улучшения PEP8")
            print("   2. Дополнительные docstrings")
            print("   3. Оптимизация производительности")
        else:
            print("🏆 ОТЛИЧНОЕ КАЧЕСТВО!")
            print("   1. Поддерживать текущий уровень")
            print("   2. Регулярные code reviews")
            print("   3. Непрерывное улучшение")

if __name__ == "__main__":
    analyzer = CodeQualityAnalyzer()
    analyzer.analyze_all_functions()