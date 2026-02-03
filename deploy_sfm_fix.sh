#!/bin/bash

echo "🚀 РАЗВЕРТЫВАНИЕ ИСПРАВЛЕНИЯ SFM ПРОБЛЕМЫ"
echo "=========================================="

echo "📤 ШАГ 1: ЗАГРУЗКА ИСПРАВЛЕННОГО ФАЙЛА"
scp -o StrictHostKeyChecking=no sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/
echo "✅ Файл загружен"

echo ""
echo "📦 ШАГ 2: УСТАНОВКА requests"
ssh -o StrictHostKeyChecking=no root@149.154.65.180 "/opt/aladdin-backend/venvs/main_env/bin/pip install requests"
echo "✅ requests установлен"

echo ""
echo "🔄 ШАГ 3: ПЕРЕЗАПУСК API GATEWAY"
ssh -o StrictHostKeyChecking=no root@149.154.65.180 "systemctl restart aladdin-main-api-gateway"
echo "⏳ Ждем запуска..."
sleep 5

echo ""
echo "📊 ШАГ 4: ПРОВЕРКА СТАТУСА"
STATUS=$(ssh -o StrictHostKeyChecking=no root@149.154.65.180 "systemctl ifi

echo ""
echo "🎯 ГОТОВ К ТЕСТИРОВАНИЮ!"
