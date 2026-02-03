#!/bin/bash

echo "🔧 ПРЯМОЙ ТЕСТ SFM HTTP API НА СЕРВЕРЕ"
echo "======================================"

echo "🧪 ТЕСТ 1: SFM Health Check"
ssh -o StrictHostKeyChecking=no root@149.154.65.180 "curl -s http://127.0.0.1:8003/api/health"

echo ""
echo "🧪 ТЕСТ 2: Прямой вызов SFM функции"
RESULT=$(ssh -o StrictHostKeyChecking=no root@149.154.65.180 "curl -s -X POST -H 'Content-Type: application/json' -d '{\"function\": \"core_base\", \"params\": {}}' http://127.0.0.1:8003/api/execute")
echo "Результат: $RESULT"

echo ""
echo "🧪 ТЕСТ 3: Проверка JSON валидности"
if echo "$RESULT" | python3 -c "import sys, json; json.load(sys.stdin); print('VALID')" 2>/dev/null; then
    echo "✅ JSON валиден"
    SUCCESS=$(echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('success', 'N/A'))Если JSON валиден и success=true, значит SFM работает корректно"
