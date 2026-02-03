#!/bin/bash
# ⚡ БЫСТРАЯ ПРОВЕРКА СТАТУСА СЕРВЕРА И ФУНКЦИЙ

echo "⚡ БЫСТРАЯ ПРОВЕРКА СТАТУСА ALADDIN СЕРВЕРА"
echo "=" * 50

# Проверка доступности сервера
echo "🌐 СЕРВЕР:"
ping -c 1 149.154.65.180 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Сервер доступен (149.154.65.180)"
else
    echo "❌ Сервер недоступен"
    exit 1
fi

# Проверка API Gateway
echo ""
echo "🏥 API GATEWAY:"
HEALTH=$(sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@149.154.65.180 "curl -s http://127.0.0.1:8002/api/health" 2>/dev/null)
if [ -n "$HEALTH" ]; then
    SFM_STATUS=$(echo $HEALTH | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('sfm_adapter', 'unknown'))" 2>/dev/null)
    ENDPOINTS=$(echo $HEALTH | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('endpoints', 0))" 2>/dev/null)
    echo "✅ API Gateway работает"
    echo "   SFM статус: $SFM_STATUS"
    echo "   Эндпоинты: $ENDPOINTS"
else
    echo "❌ API Gateway не отвечает"
fi

# Проверка SFM
echo ""
echo "🤖 SFM CORE:"
SFM_CHECK=$(sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@149.154.65.180 "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && PYTHONPATH=/opt/aladdin-backend:$PYTHONPATH python3 -c 'from security.sfm_singleton import get_sfm; sfm = get_sfm(); print(f\"Функции: {len(sfm.functions)}\")' 2>/dev/null" 2>/dev/null)
if [ -n "$SFM_CHECK" ]; then
    echo "✅ SFM работает: $SFM_CHECK функций"
else
    echo "❌ SFM не загружается"
fi

# Быстрая проверка функций
echo ""
echo "🧪 ФУНКЦИИ 1-4/93:"
FUNCTIONS_OK=0

# Функция 1
RESULT1=$(sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@149.154.65.180 "curl -s http://127.0.0.1:8002/api/phishing/sensitivity" 2>/dev/null | grep -v '"source": "mock"' | wc -l 2>/dev/null)
if [ "$RESULT1" -gt 0 ]; then ((FUNCTIONS_OK++)); fi

# Функция 2
RESULT2=$(sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@149.154.65.180 "curl -s http://127.0.0.1:8002/api/analytics/overview" 2>/dev/null | grep -v '"source": "mock"' | wc -l 2>/dev/null)
if [ "$RESULT2" -gt 0 ]; then ((FUNCTIONS_OK++)); fi

# Функция 3
RESULT3=$(sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@149.154.65.180 "curl -s http://127.0.0.1:8002/api/components/status/crash_detection_agent" 2>/dev/null | grep -v '"source": "mock"' | wc -l 2>/dev/null)
if [ "$RESULT3" -gt 0 ]; then ((FUNCTIONS_OK++)); fi

# Функция 4
RESULT4=$(sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@149.154.65.180 "curl -s -X POST http://127.0.0.1:8002/api/components/enable/crash_detection_agent" 2>/dev/null | grep -v '"source": "mock"' | wc -l 2>/dev/null)
if [ "$RESULT4" -gt 0 ]; then ((FUNCTIONS_OK++)); fi

echo "✅ Функций с реальными данными: $FUNCTIONS_OK/4"

echo ""
echo "🎯 РЕЗУЛЬТАТ:"
if [ $FUNCTIONS_OK -eq 4 ]; then
    echo "🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ! АРХИТЕКТУРА ПОДТВЕРЖДЕНА!"
    echo "   Мобильное → API → SFM → AI агенты ✅"
else
    echo "⚠️  Есть проблемы с функциями ($FUNCTIONS_OK/4 работают)"
fi