# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Code Quality Configuration
Конфигурация контроля качества кода Python

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

# Конфигурация инструментов контроля качества
QUALITY_TOOLS_CONFIG = {
    "flake8": {
        "enabled": True,
        "max_line_length": 88,  # Black стандарт
        "ignore": [
            "E501",  # Слишком длинные строки
            "W503",  # Разрыв строки перед бинарным оператором
            "E203",  # Пробелы перед двоеточием
        ],
        "max_complexity": 10,
        "timeout": 30,
    },
    "pylint": {
        "enabled": True,
        "max_score": 8.0,
        "disable": [
            "C0114",  # Missing module docstring
            "C0116",  # Missing function docstring
            "R0903",  # Too few public methods
            "R0913",  # Too many arguments
        ],
        "timeout": 60,
    },
    "black": {"enabled": True, "line_length": 88, "timeout": 30},
    "mypy": {
        "enabled": True,
        "strict": False,
        "ignore_missing_imports": True,
        "timeout": 60
    },
    "isort": {
        "enabled": True,
        "profile": "black",
        "line_length": 88,
        "timeout": 30
    },
}

# Стандарты качества
QUALITY_STANDARDS = {
    "excellent": {
        "min_score": 95.0,
        "grade": "A+",
        "description": "Отличное качество кода"},
    "good": {
        "min_score": 85.0,
        "grade": "A",
        "description": "Хорошее качество кода"},
    "satisfactory": {
        "min_score": 75.0,
        "grade": "B",
        "description": "Удовлетворительное качество кода"},
    "needs_improvement": {
        "min_score": 60.0,
        "grade": "C",
        "description": "Требует улучшения"},
    "poor": {
        "min_score": 0.0,
        "grade": "F",
        "description": "Плохое качество кода"},
}

# Исключения для анализа
EXCLUDE_PATTERNS = [
    "__pycache__",
    "venv",
    "env",
    ".git",
    ".vscode",
    "node_modules",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
]

# Настройки отчетов
REPORT_SETTINGS = {
    "max_files_in_summary": 10,
    "include_details": True,
    "save_reports": True,
    "reports_directory": "quality_reports",
    "auto_fix": False,  # Автоматическое исправление проблем
}

# Цветовая схема для отчетов
REPORT_COLORS = {
    "excellent": "🟢",
    "good": "🟡",
    "satisfactory": "🟠",
    "needs_improvement": "🔴",
    "poor": "⚫"}
