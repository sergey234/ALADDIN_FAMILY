#!/bin/bash
# Прямой подсчет функций в SFM на сервере

# Попытка автоматически найти сервер из документации
SERVER_IP="149.154.65.180"
SERVER_USER="root"

echo "================================================================================"
echo "🔍 ПРЯМОЙ ПОДСЧЕТ ФУНКЦИЙ В SFM"
echo "================================================================================"
echo ""

# Попытка подключения к серверу
echo "📡 Попытка подключения к серверу ${SERVER_USER}@${SERVER_IP}..."
echo ""

ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF' 2>/dev/null
    REGISTRY_PATH="/opt/aladdin-backend/data/sfm/function_registry.json"
    
    if [ ! -f "$REGISTRY_PATH" ]; then
        echo "❌ Registry не найден: $REGISTRY_PATH"
        exit 1
    fi
    
    python3 << 'PYEOF'
import json
import sys
from pathlib import Path

try:
    registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Определение структуры
    if isinstance(registry, list):
        agents = registry
    elif isinstance(registry, dict):
        if "agents" in registry:
            agents = registry["agents"]
        else:
            agents = [v for v in registry.values() if isinstance(v, dict) and "functions" in v]
    else:
        agents = []
    
    total_agents = len(agents)
    total_functions = 0
    active_agents = 0
    agents_info = []
    
    for agent in agents:
        if isinstance(agent, dict):
            agent_name = agent.get("name", "unknown")
            functions = agent.get("functions", [])
            func_count = len(functions)
            total_functions += func_count
            status = agent.get("status", "unknown")
            
            if status == "active":
                active_agents += 1
            
            agents_info.append({
                "name": agent_name,
                "functions": func_count,
                "status": status
            })
    
    # Сортировка
    agents_info.sort(key=lambda x: x["functions"], reverse=True)
    
    print("=" * 80)
    print("📊 ТОЧНАЯ СТАТИСТИКА SFM:")
    print("=" * 80)
    print(f"Всего агентов: {total_agents}")
    print(f"Активных агентов: {active_agents}")
    print(f"ВСЕГО ФУНКЦИЙ: {total_functions}")
    print("=" * 80)
    print()
    print("🏆 ТОП-30 АГЕНТОВ ПО КОЛИЧЕСТВУ ФУНКЦИЙ:")
    print()
    for i, info in enumerate(agents_info[:30], 1):
        status_icon = "✅" if info["status"] == "active" else "⚠️"
        print(f"  {i:3d}. {status_icon} {info['name']:50s} - {info['functions']:4d} функций")
    
    if len(agents_info) > 30:
        print(f"  ... и еще {len(agents_info) - 30} агентов")
    
    print()
    print("=" * 80)
    print(f"✅ ИТОГО: {total_functions} ФУНКЦИЙ")
    print("=" * 80)
    
    # Сохраняем результат для дальнейшего использования
    result = {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_functions": total_functions,
        "timestamp": str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else ""
    }
    
    sys.exit(0)
PYEOF

EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Подсчет завершен успешно!"
else
    echo ""
    echo "❌ Не удалось подключиться к серверу"
    echo "   Попробуйте указать сервер вручную:"
    echo "   export ALADDIN_SERVER=your-server.com"
    echo "   export ALADDIN_SERVER_USER=root"
    echo "   ./check_sfm_on_server.sh"
fi
