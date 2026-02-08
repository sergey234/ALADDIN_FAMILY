#!/bin/bash

echo "🔍 ПРОВЕРКА SFM REGISTRY НА СЕРВЕРЕ"
echo "=================================="
echo ""

SERVER="root@149.154.65.180"
SFM_REGISTRY="/opt/aladdin-backend/data/sfm/function_registry.json"

echo "📋 Подключаемся к серверу: $SERVER"
echo "📁 Путь к registry: $SFM_REGISTRY"
echo ""

echo "🧪 ТЕСТ 1: Проверка существования файла registry"
ssh -o StrictHostKeyChecking=no $SERVER "ls -la $SFM_REGISTRY" 2>/dev/null || echo "❌ Файл registry не найден"

echo ""
echo "🧪 ТЕСТ 2: Чтение структуры registry"
REGISTRY_CONTENT=$(ssh -o StrictHostKeyChecking=no $SERVER "cat $SFM_REGISTRY 2>/dev/null | head -50")

if [ -z "$REGISTRY_CONTENT" ]; then
    echo "❌ Не удалось прочитать registry"
else
    echo "✅ Registry найден. Первые 50 строк:"
    echo "$REGISTRY_CONTENT"
    echo ""

    echo "🧪 ТЕСТ 3: Подсчет агентов и функций"
    AGENTS_COUNT=$(ssh -o StrictHostKeyChecking=no $SERVER "python3 -c 'import json; f=open(\"$SFM_REGISTRY\"); data=json.load(f); f.close(); print(len(data.get(\"agents\", [])) if isinstance(data, dict) and \"agents\" in data else len(data) if isinstance(data, list) else 0)' 2>/dev/null || echo "0")
    echo "Количество агентов: $AGENTS_COUNT"

    FUNCTIONS_COUNT=$(ssh -o StrictHostKeyChecking=no $SERVER "python3 -c 'import json; f=open(\"$SFM_REGISTRY\"); data=json.load(f); f.close(); count=0; items=data.get(\"agents\", data) if isinstance(data, dict) else data; [count := count + len(agent.get(\"functions\", [])) for agent in items if isinstance(agent, dict)]; print(count)' 2>/dev/null || echo "0")
    echo "Количество функций: $FUNCTIONS_COUNT"
fi

echo ""
echo "🧪 ТЕСТ 4: Проверка SFM сервиса"
ssh -o StrictHostKeyChecking=no $SERVER "systemctl status sfm-core 2>/dev/null | head -3" || echo "⚠️ SFM сервис не найден"

echo ""
echo "🧪 ТЕСТ 5: Проверка backend сервиса"
ssh -o StrictHostKeyChecking=no $SERVER "systemctl status aladdin-backend 2>/dev/null | grep Active" || echo "⚠️ Backend сервис не найден"

echo ""
echo "✅ Проверка завершена!"