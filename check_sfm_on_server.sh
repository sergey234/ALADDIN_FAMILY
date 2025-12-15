#!/bin/bash
# Скрипт для проверки реального количества функций в SFM на сервере

SERVER="${ALADDIN_SERVER:-your-server.com}"
SERVER_USER="${ALADDIN_SERVER_USER:-root}"

echo "================================================================================"
echo "🔍 ПРОВЕРКА РЕАЛЬНОГО КОЛИЧЕСТВА ФУНКЦИЙ В SFM НА СЕРВЕРЕ"
echo "================================================================================"
echo ""

if [ "$SERVER" == "your-server.com" ]; then
    echo "⚠️  Укажите сервер:"
    echo "   export ALADDIN_SERVER=your-server.com"
    echo "   export ALADDIN_SERVER_USER=root"
    echo ""
    read -p "Введите адрес сервера: " SERVER
    read -p "Введите пользователя (по умолчанию root): " SERVER_USER
    SERVER_USER=${SERVER_USER:-root}
fi

echo "📡 Подключение к серверу: ${SERVER_USER}@${SERVER}"
echo ""

# Копируем скрипт на сервер
scp count_sfm_functions.py ${SERVER_USER}@${SERVER}:/tmp/ 2>/dev/null || echo "⚠️  Не удалось скопировать скрипт"

# Запускаем проверку на сервере
ssh ${SERVER_USER}@${SERVER} << 'EOF'
    echo "🔍 Проверка SFM на сервере..."
    echo ""
    
    REGISTRY_PATH="/opt/aladdin-backend/data/sfm/function_registry.json"
    
    if [ ! -f "$REGISTRY_PATH" ]; then
        echo "❌ Registry не найден: $REGISTRY_PATH"
        exit 1
    fi
    
    echo "✅ Registry найден: $REGISTRY_PATH"
    FILE_SIZE=$(stat -f%z "$REGISTRY_PATH" 2>/dev/null || stat -c%s "$REGISTRY_PATH" 2>/dev/null)
    LINES=$(wc -l < "$REGISTRY_PATH")
    echo "   Размер файла: $FILE_SIZE байт"
    echo "   Строк в файле: $LINES"
    echo ""
    
    # Подсчет через Python
    python3 << 'PYEOF'
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")

try:
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Определение структуры
    if isinstance(registry, list):
        agents = registry
    elif isinstance(registry, dict):
        if "agents" in registry:
            agents = registry["agents"]
        else:
            agents = [v for v in registry.values() if isinstance(v, dict)]
    else:
        agents = []
    
    total_agents = len(agents)
    total_functions = 0
    agents_info = []
    
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
    
    # Сортировка по количеству функций
    agents_info.sort(key=lambda x: x["functions"], reverse=True)
    
    print("=" * 80)
    print("📊 РЕАЛЬНАЯ СТАТИСТИКА SFM НА СЕРВЕРЕ:")
    print("=" * 80)
    print(f"Всего агентов: {total_agents}")
    print(f"Всего функций: {total_functions}")
    print()
    
    print("🏆 ТОП-20 АГЕНТОВ ПО КОЛИЧЕСТВУ ФУНКЦИЙ:")
    print()
    for i, info in enumerate(agents_info[:20], 1):
        status_icon = "✅" if info["status"] == "active" else "⚠️"
        print(f"  {i:3d}. {status_icon} {info['name']:50s} - {info['functions']:4d} функций")
    
    if len(agents_info) > 20:
        print(f"  ... и еще {len(agents_info) - 20} агентов")
    
    print()
    print("=" * 80)
    print(f"✅ ПОДТВЕРЖДЕНО: Всего {total_functions} функций в SFM")
    print("=" * 80)
    
PYEOF
    
EOF

echo ""
echo "✅ Проверка завершена!"
