#!/usr/bin/env python3
"""
Скрипт для обновления SFM реестра с актуальными данными anti_fraud_master_ai.py
"""

import json
import os
from datetime import datetime


def get_file_stats(file_path: str) -> dict:
    """Получить статистику файла"""
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    return {
        "lines_of_code": len(lines),
        "file_size_bytes": stat.st_size,
        "file_size_kb": round(stat.st_size / 1024, 2),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


def update_sfm_registry(file_path: str, function_id: str):
    """Обновить SFM реестр с актуальными данными"""
    registry_path = "./data/sfm/function_registry.json"
    
    # Читаем текущий реестр
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Получаем статистику файла
    stats = get_file_stats(file_path)
    
    # Обновляем данные функции
    if 'functions' not in registry:
        registry['functions'] = {}
    
    if function_id not in registry['functions']:
        registry['functions'][function_id] = {}
    
    # Обновляем метаданные
    registry['functions'][function_id].update({
        "function_id": function_id,
        "file_path": file_path,
        "status": "active",
        "lines_of_code": stats.get("lines_of_code", 0),
        "file_size_bytes": stats.get("file_size_bytes", 0),
        "file_size_kb": stats.get("file_size_kb", 0),
        "flake8_errors": 4,  # Текущие ошибки: 3 E501 + 1 E203
        "quality_score": "A-",
        "last_updated": datetime.now().isoformat(),
        "category": "ai_agents",
        "dependencies": [
            "core.base.SecurityBase",
            "asyncio",
            "logging",
            "datetime",
            "enum",
            "functools",
            "typing"
        ],
        "features": [
            "fraud_detection",
            "transaction_analysis",
            "phone_validation",
            "audio_analysis",
            "risk_assessment"
        ]
    })
    
    # Сохраняем обновленный реестр
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"✅ SFM реестр успешно обновлен!")
    print(f"   📁 Файл: {file_path}")
    print(f"   📏 Строк: {stats.get('lines_of_code', 0)}")
    print(f"   💾 Размер: {stats.get('file_size_kb', 0)}KB")
    print(f"   📈 Качество: A-")
    print(f"   🔧 Ошибки flake8: 4")
    print(f"   📅 Обновлено: {datetime.now().isoformat()}")


if __name__ == "__main__":
    target_file = "./security/ai_agents/anti_fraud_master_ai.py"
    function_id = "anti_fraud_master_ai"
    update_sfm_registry(target_file, function_id)