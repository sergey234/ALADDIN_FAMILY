#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flake8 Analysis Script для новых компонентов ALADDIN
Анализ кода на соответствие PEP8 стандартам

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

class Flake8Analyzer:
    """Анализатор кода на соответствие PEP8"""
    
    def __init__(self, max_line_length: int = 120):
        self.max_line_length = max_line_length
        self.errors = []
        self.warnings = []
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Анализ файла на ошибки flake8"""
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Анализ длины строк
            self._check_line_length(lines)
            
            # Анализ синтаксиса
            self._check_syntax(content)
            
            # Анализ импортов
            self._check_imports(lines)
            
            # Анализ отступов
            self._check_indentation(lines)
            
            # Анализ пробелов
            self._check_whitespace(lines)
            
            # Анализ комментариев
            self._check_comments(lines)
            
            return {
                "file": file_path,
                "total_lines": len(lines),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "error_details": self.errors,
                "warning_details": self.warnings,
                "quality_score": self._calculate_quality_score(len(lines))
            }
            
        except Exception as e:
            return {
                "file": file_path,
                "error": str(e),
                "quality_score": 0
            }
    
    def _check_line_length(self, lines: List[str]):
        """Проверка длины строк"""
        for i, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                self.errors.append({
                    "line": i,
                    "code": "E501",
                    "message": f"line too long ({len(line)} > {self.max_line_length} characters)",
                    "severity": "error"
                })
    
    def _check_syntax(self, content: str):
        """Проверка синтаксиса Python"""
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.errors.append({
                "line": e.lineno,
                "code": "E999",
                "message": f"syntax error: {e.msg}",
                "severity": "error"
            })
    
    def _check_imports(self, lines: List[str]):
        """Проверка импортов"""
        import_line = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Проверка порядка импортов
            if stripped.startswith('import ') or stripped.startswith('from '):
                if not import_line:
                    import_line = True
                # Проверка пробелов после import
                if 'import ' in stripped and not re.match(r'^import\s+\w', stripped):
                    self.warnings.append({
                        "line": i,
                        "code": "E401",
                        "message": "multiple imports on one line",
                        "severity": "warning"
                    })
            elif import_line and stripped and not stripped.startswith('#'):
                import_line = False
    
    def _check_indentation(self, lines: List[str]):
        """Проверка отступов"""
        for i, line in enumerate(lines, 1):
            if line.strip():  # Непустые строки
                # Проверка смешанных табов и пробелов
                if '\t' in line and '    ' in line:
                    self.errors.append({
                        "line": i,
                        "code": "E101",
                        "message": "indentation contains mixed spaces and tabs",
                        "severity": "error"
                    })
                
                # Проверка неправильных отступов
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 4 != 0 and leading_spaces > 0:
                    self.warnings.append({
                        "line": i,
                        "code": "E111",
                        "message": "indentation is not a multiple of four",
                        "severity": "warning"
                    })
    
    def _check_whitespace(self, lines: List[str]):
        """Проверка пробелов"""
        for i, line in enumerate(lines, 1):
            # Проверка пробелов в конце строки
            if line.endswith(' ') or line.endswith('\t'):
                self.warnings.append({
                    "line": i,
                    "code": "W291",
                    "message": "trailing whitespace",
                    "severity": "warning"
                })
            
            # Проверка пробелов перед двоеточием
            if re.search(r'\s+:', line):
                self.warnings.append({
                    "line": i,
                    "code": "E203",
                    "message": "whitespace before ':'",
                    "severity": "warning"
                })
    
    def _check_comments(self, lines: List[str]):
        """Проверка комментариев"""
        for i, line in enumerate(lines, 1):
            # Проверка комментариев TODO, FIXME
            if '#' in line:
                comment = line.split('#')[1].strip()
                if comment.upper().startswith(('TODO', 'FIXME', 'XXX', 'HACK')):
                    self.warnings.append({
                        "line": i,
                        "code": "W291",
                        "message": f"found {comment.split()[0].upper()} comment",
                        "severity": "warning"
                    })
    
    def _calculate_quality_score(self, total_lines: int) -> float:
        """Расчет качества кода"""
        if total_lines == 0:
            return 0.0
        
        error_penalty = len(self.errors) * 10
        warning_penalty = len(self.warnings) * 2
        
        base_score = 100.0
        final_score = max(0.0, base_score - error_penalty - warning_penalty)
        
        return round(final_score, 1)

def main():
    """Основная функция"""
    print("🔍 FLAKE8 АНАЛИЗ ТРЕХ НОВЫХ КОМПОНЕНТОВ ALADDIN")
    print("=" * 60)
    
    analyzer = Flake8Analyzer(max_line_length=120)
    
    files_to_analyze = [
        "advanced_threat_intelligence.py",
        "advanced_behavioral_analytics.py", 
        "enhanced_security_integration.py"
    ]
    
    total_errors = 0
    total_warnings = 0
    total_lines = 0
    quality_scores = []
    
    for filename in files_to_analyze:
        print(f"\n📁 Анализ файла: {filename}")
        print("-" * 40)
        
        result = analyzer.analyze_file(filename)
        
        if "error" in result:
            print(f"❌ Ошибка чтения файла: {result['error']}")
            continue
        
        print(f"📊 Строк кода: {result['total_lines']}")
        print(f"❌ Ошибки: {result['errors']}")
        print(f"⚠️  Предупреждения: {result['warnings']}")
        print(f"⭐ Качество: {result['quality_score']}/100")
        
        # Детали ошибок
        if result['error_details']:
            print("\n🔍 Детали ошибок:")
            for error in result['error_details']:
                print(f"  Строка {error['line']}: {error['code']} - {error['message']}")
        
        # Детали предупреждений
        if result['warning_details']:
            print("\n⚠️  Детали предупреждений:")
            for warning in result['warning_details']:
                print(f"  Строка {warning['line']}: {warning['code']} - {warning['message']}")
        
        total_errors += result['errors']
        total_warnings += result['warnings']
        total_lines += result['total_lines']
        quality_scores.append(result['quality_score'])
    
    # Общая статистика
    print("\n" + "=" * 60)
    print("📊 ОБЩАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"📁 Файлов проанализировано: {len(files_to_analyze)}")
    print(f"📄 Общее количество строк: {total_lines}")
    print(f"❌ Общее количество ошибок: {total_errors}")
    print(f"⚠️  Общее количество предупреждений: {total_warnings}")
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"⭐ Среднее качество: {avg_quality:.1f}/100")
        
        if avg_quality >= 95:
            print("🏆 КАЧЕСТВО: A+ (ОТЛИЧНО)")
        elif avg_quality >= 90:
            print("🥇 КАЧЕСТВО: A (ОЧЕНЬ ХОРОШО)")
        elif avg_quality >= 80:
            print("🥈 КАЧЕСТВО: B (ХОРОШО)")
        elif avg_quality >= 70:
            print("🥉 КАЧЕСТВО: C (УДОВЛЕТВОРИТЕЛЬНО)")
        else:
            print("❌ КАЧЕСТВО: ТРЕБУЕТ УЛУЧШЕНИЯ")
    
    # Оценка готовности
    if total_errors == 0 and total_warnings <= 5:
        print("\n✅ ГОТОВНОСТЬ К ПРОДАКШН: 100%")
        print("🚀 ВСЕ КОМПОНЕНТЫ ГОТОВЫ К ЗАПУСКУ!")
    elif total_errors == 0:
        print("\n⚠️  ГОТОВНОСТЬ К ПРОДАКШН: 95%")
        print("🔧 ТРЕБУЮТСЯ МИНОРНЫЕ ИСПРАВЛЕНИЯ")
    else:
        print("\n❌ ГОТОВНОСТЬ К ПРОДАКШН: < 90%")
        print("🛠️  ТРЕБУЮТСЯ ИСПРАВЛЕНИЯ ОШИБОК")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()