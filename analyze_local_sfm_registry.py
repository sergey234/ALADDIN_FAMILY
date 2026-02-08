#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ локального SFM registry из entry файлов
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_local_sfm_registry():
    """Анализ всех локальных function registry entry файлов"""

    print("🔍 АНАЛИЗ ЛОКАЛЬНОГО SFM REGISTRY")
    print("=" * 60)
    print()

    # Путь к папке с registry файлами
    registry_dir = Path("security/ai_agents")

    if not registry_dir.exists():
        print(f"❌ Папка {registry_dir} не найдена!")
        return

    # Поиск всех registry файлов
    registry_files = list(registry_dir.glob("function_registry_entry_*.json"))

    print(f"📁 Найдено registry файлов: {len(registry_files)}")
    print()

    total_agents = 0
    total_functions = 0
    total_endpoints = 0
    agents_data = []

    # Анализ каждого файла
    for registry_file in sorted(registry_files):
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            agent_name = data.get("name", "unknown")
            agent_type = data.get("type", "unknown")
            status = data.get("status", "unknown")
            functions = data.get("functions", [])
            api_endpoints = data.get("api_endpoints", [])

            func_count = len(functions)
            endpoint_count = len(api_endpoints)

            total_agents += 1
            total_functions += func_count
            total_endpoints += endpoint_count

            agents_data.append({
                "name": agent_name,
                "type": agent_type,
                "status": status,
                "functions": func_count,
                "endpoints": endpoint_count,
                "file": registry_file.name
            })

            status_icon = "✅" if status == "active" else "⚠️" if status == "inactive" else "❌"
            print(f"  {status_icon} {agent_name:35s} - {func_count:2d} функций, {endpoint_count:2d} endpoints")

        except Exception as e:
            print(f"  ❌ Ошибка чтения {registry_file}: {e}")

    print()
    print("=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА ЛОКАЛЬНОГО REGISTRY")
    print("=" * 60)
    print(f"  Всего агентов: {total_agents}")
    print(f"  Всего функций: {total_functions}")
    print(f"  Всего API endpoints: {total_endpoints}")
    print()

    # Группировка по статусу
    status_stats = defaultdict(int)
    type_stats = defaultdict(int)

    for agent in agents_data:
        status_stats[agent["status"]] += 1
        type_stats[agent["type"]] += 1

    print("📈 СТАТИСТИКА ПО СТАТУСУ:")
    for status, count in status_stats.items():
        icon = "✅" if status == "active" else "⚠️" if status == "inactive" else "❌"
        print(f"  {icon} {status}: {count} агентов")

    print()
    print("📈 СТАТИСТИКА ПО ТИПУ:")
    for agent_type, count in type_stats.items():
        print(f"  • {agent_type}: {count} агентов")

    print()
    print("=" * 60)
    print()

    # Детальный анализ топ агентов
    print("🏆 ТОП АГЕНТОВ ПО КОЛИЧЕСТВУ ФУНКЦИЙ:")
    print()

    sorted_agents = sorted(agents_data, key=lambda x: x["functions"], reverse=True)

    for i, agent in enumerate(sorted_agents[:10], 1):
        status_icon = "✅" if agent["status"] == "active" else "⚠️" if agent["status"] == "inactive" else "❌"
        print(f"  {i:2d}. {status_icon} {agent['name']:35s} - {agent['functions']:3d} функций, {agent['endpoints']:2d} endpoints")

    print()
    print("💡 Для проверки SFM registry на сервере запустите:")
    print("   ./check_sfm_registry_server.expect")
    print()

    return agents_data, total_agents, total_functions, total_endpoints

if __name__ == "__main__":
    analyze_local_sfm_registry()