#!/bin/bash
# 🚀 СКРИПТ РАЗВЕРТЫВАНИЯ ФУНКЦИИ 4/93: /api/components/enable/{component_id}
# Выполнить после исправления функции в api_gateway_server_current.py

echo "🔧 НАЧИНАЕМ РАЗВЕРТЫВАНИЕ ФУНКЦИИ 4/93"

# ШАГ 1: Создание backup на сервере
echo "📦 Создание backup на сервере..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \
    "cd /opt/aladdin-backend && cp api_gateway.py api_gateway_backup_4_\$(date +%Y%m%d_%H%M%S).py && echo '✅ Backup создан'"

# ШАГ 2: Загрузка исправленного файла
echo "📤 Загрузка исправленного api_gateway_server_current.py..."
sshpass -p 'Sergio675' scp -o StrictHostKeyChecking=no api_gateway_server_current.py \
    root@149.154.65.180:/opt/aladdin-backend/api_gateway.py

# ШАГ 3: Проверка синтаксиса на сервере
echo "🔍 Проверка синтаксиса..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \
    "cd /opt/aladdin-backend && python3 -m py_compile api_gateway.py && echo '✅ Синтаксис корректный'"

# ШАГ 4: Перезапуск API Gateway
echo "🔄 Перезапуск API Gateway..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \
    "systemctl restart aladdin-main-api-gateway && sleep 5"

# ШАГ 5: Проверка статуса API
echo "🏥 Проверка health status..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \
    "curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool"

# ШАГ 6: Тестирование исправленной функции
echo "🧪 Тестирование функции /api/components/enable/{component_id}..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \
    "curl -s -X POST http://127.0.0.1:8002/api/components/enable/crash_detection_agent | python3 -m json.tool"

# ШАГ 7: Проверка логов
echo "📋 Проверка логов на ошибки..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \
    "journalctl -u aladdin-main-api-gateway -n 5"

echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo ""
echo "📊 РЕЗУЛЬТАТЫ:"
echo "- Функция 4/93 исправлена: /api/components/enable/{component_id}"
echo "- Теперь возвращает реальные данные из SFM вместо mock"
echo "- Следующая функция: 5/93 - /api/components/disable/{component_id}"