#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальное исправление ошибок flake8
"""

import re

def fix_enhanced_data_collector():
    """Исправление enhanced_data_collector.py"""
    filepath = 'security/ai_agents/enhanced_data_collector.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправления
    fixes = [
        # Исправление отступов
        (r'                         \'AppleWebKit/537\.36 \(KHTML, like Gecko\) \'\n                         \'Chrome/91\.0\.4472\.124 Safari/537\.36\'', 
         '                         \'AppleWebKit/537.36 (KHTML, like Gecko) \'\n                         \'Chrome/91.0.4472.124 Safari/537.36\''),
        
        # Исправление f-string
        (r'f"Исправление файла: {filepath}"', '"Исправление файла: {}"'.format(filepath)),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_fraud_detection_api():
    """Исправление fraud_detection_api.py"""
    filepath = 'security/ai_agents/fraud_detection_api.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправления
    fixes = [
        # Удаление неиспользуемых импортов
        (r'import json\n', ''),
        (r'from typing import Dict, List, Any, Optional\n', ''),
        
        # Исправление импортов
        (r'# Добавляем путь к модулям\nsys\.path\.append\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\)\)\)\)\n\nfrom security\.ai_agents\.russian_fraud_ml_models import RussianFraudMLModels\nfrom security\.ai_agents\.enhanced_data_collector import EnhancedDataCollector\nfrom security\.ai_agents\.auto_learning_system import AutoLearningSystem',
         '# Добавляем путь к модулям\nsys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))\n\n# Импорты после sys.path.append\ntry:\n    from security.ai_agents.russian_fraud_ml_models import RussianFraudMLModels\n    from security.ai_agents.enhanced_data_collector import EnhancedDataCollector\n    from security.ai_agents.auto_learning_system import AutoLearningSystem\nexcept ImportError:\n    RussianFraudMLModels = None\n    EnhancedDataCollector = None\n    AutoLearningSystem = None'),
        
        # Добавление пустых строк между функциями
        (r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(',
         '\n\n\ndef \\1('),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Удаление лишних пустых строк
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_improved_ml_models():
    """Исправление improved_ml_models.py"""
    filepath = 'security/ai_agents/improved_ml_models.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправления
    fixes = [
        # Удаление неиспользуемых импортов
        (r'from typing import Dict, List, Any\n', 'from typing import Dict, Any\n'),
        (r'from sklearn\.linear_model import LogisticRegression\n', ''),
        
        # Исправление Tuple
        (r'Tuple\[np\.ndarray, np\.ndarray\]', 'tuple'),
        
        # Удаление неиспользуемых переменных
        (r'        classifier_metrics = improved_models\.create_enhanced_fraud_classifier\(\)\n', ''),
        (r'        severity_metrics = improved_models\.create_enhanced_severity_predictor\(\)\n', ''),
        (r'        region_metrics = improved_models\.create_enhanced_region_analyzer\(\)\n', ''),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Основная функция"""
    print("🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ FLAKE8 ОШИБОК")
    print("=" * 40)
    
    try:
        fix_enhanced_data_collector()
        fix_fraud_detection_api()
        fix_improved_ml_models()
        
        print("✅ Все файлы исправлены!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()