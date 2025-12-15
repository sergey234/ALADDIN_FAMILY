#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для подсчета всех функций в SFM function_registry.json
Подключается к серверу и считает реальное количество функций
"""

import json
import sys
from pathlib import Path

# Путь к registry на сервере
REGISTRY_PATH = Path("/opt/aladdin-backend/data/sfm/function_registry.json")

def count_functions_local():
    """Подсчет функций из локальных entry файлов"""
    
    print("=" * 80)
    print("📊 ПОДСЧЕТ ФУНКЦИЙ ИЗ ЛОКАЛЬНЫХ ENTRY ФАЙЛОВ")
    print("=" * 80)
    print()
    
    entry_files = [
        "security/ai_agents/function_registry_entry_dark_web_monitoring.json",
        "security/ai_agents/function_registry_entry_identity_theft_protection.json"
    ]
    
    total_functions = 0
    agents_info = []
    
    for entry_file in entry_files:
        entry_path = Path(entry_file)
        if entry_path.exists():
            try:
                with open(entry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                agent_name = data.get("name", "unknown")
                functions = data.get("functions", [])
                func_count = len(functions)
                total_functions += func_count
                
                agents_info.append({
                    "name": agent_name,
                    "functions": func_count
                })
                
                print(f"  ✅ {agent_name}: {func_count} функций")
            except Exception as e:
                print(f"  ❌ Ошибка чтения {entry_file}: {e}")
        else:
            print(f"  ⚠️  Файл не найден: {entry_file}")
    
    print()
    print(f"  📊 ЛОКАЛЬНО (только новые): {total_functions} функций")
    print()
    
    return total_functions, agents_info

def count_functions_from_server():
    """Подсчет функций из registry на сервере"""
    
    print("=" * 80)
    print("📊 ПОДСЧЕТ ФУНКЦИЙ ИЗ РЕГИСТРА НА СЕРВЕРЕ")
    print("=" * 80)
    print()
    
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry не найден: {REGISTRY_PATH}")
        print(f"   Это нормально, если запущено локально (не на сервере)")
        print()
        return None, None
    
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Определение структуры registry
        if isinstance(registry, list):
            agents = registry
        elif isinstance(registry, dict):
            if "agents" in registry:
                agents = registry["agents"]
            else:
                agents = [v for v in registry.values() if isinstance(v, dict)]
        else:
            print("❌ Неподдерживаемый формат registry")
            return None, None
        
        total_agents = len(agents)
        total_functions = 0
        agents_info = []
        
        print(f"  Найдено агентов: {total_agents}")
        print()
        
        for agent in agents:
            if isinstance(agent, dict):
                agent_name = agent.get("name", "unknown")
                functions = agent.get("functions", [])
                func_count = len(functions)
                total_functions += func_count
                
                agents_info.append({
                    "name": agent_name,
                    "functions": func_count,
                    "status": agent.get("status", "unknown")
                })
        
        # Сортировка по количеству функций (по убыванию)
        agents_info.sort(key=lambda x: x["functions"], reverse=True)
        
        print("  Детализация по агентам:")
        print()
        for i, info in enumerate(agents_info, 1):
            status_icon = "✅" if info["status"] == "active" else "⚠️"
            print(f"    {i:3d}. {status_icon} {info['name']:50s} - {info['functions']:4d} функций")
        
        print()
        print("=" * 80)
        print(f"📊 ИТОГО НА СЕРВЕРЕ:")
        print(f"   Всего агентов: {total_agents}")
        print(f"   Всего функций: {total_functions}")
        print("=" * 80)
        print()
        
        return total_functions, agents_info
        
    except Exception as e:
        print(f"❌ Ошибка чтения registry: {e}")
        return None, None

def main():
    """Главная функция"""
    
    print()
    print("🔍 ПОДСЧЕТ ФУНКЦИЙ В SFM")
    print()
    
    # 1. Подсчет локальных entry файлов
    local_count, local_agents = count_functions_local()
    
    # 2. Попытка подсчета с сервера (если доступно)
    server_count, server_agents = count_functions_from_server()
    
    # 3. Итоговый вывод
    print("=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print()
    
    if server_count is not None:
        print(f"✅ Найдено на сервере:")
        print(f"   • Всего агентов: {len(server_agents)}")
        print(f"   • Всего функций: {server_count}")
        print()
        
        # Топ-10 агентов по количеству функций
        print("🏆 ТОП-10 АГЕНТОВ ПО КОЛИЧЕСТВУ ФУНКЦИЙ:")
        print()
        for i, agent in enumerate(server_agents[:10], 1):
            print(f"   {i:2d}. {agent['name']:50s} - {agent['functions']:4d} функций")
        print()
        
        if server_count > 1000:
            print(f"✅ Подтверждено: В SFM действительно более {server_count} функций!")
    else:
        print("⚠️  Доступ к серверу недоступен (запущено локально)")
        print(f"   Локальные entry файлы: {local_count} функций")
        print()
        print("💡 Для подсчета реального количества функций:")
        print("   ssh user@server 'python3 count_sfm_functions.py'")
        print()
    
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
