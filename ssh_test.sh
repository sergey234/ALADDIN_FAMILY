#!/bin/bash

echo "🔌 SSH ПОДКЛЮЧЕНИЕ К СЕРВЕРУ ALADDIN"
echo "===================================="

# Проверяем статус сервисов
echo "📊 ПРОВЕРКА СТАТУСА СЕРВИСОВ:"

# API Gateway
echo "🔍 API Gateway:"
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@149.154.65.180 "systemctl status aladdin-main-api-gateway --no-pager | head -3"

# SFM HTTP API
echo ""
echo "🔍 SFM HTTP API:"
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@149.154.65.180 "systemctl status aladdin-sfm-core --no-pager | head -3"

# Проверяем порты
echo ""
echo "🔍 ОТКРЫТЫЕ ПОРТЫ:"
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@149.154.65.180 "ss -tlnp | grep -E ':800[23]'"

# Тестируем API локально на сервере
echo ""
echo "🧪 ТЕСТИРОВАНИЕ API (локально наК ПОЛНОМУ ТЕСТИРОВАНИЮ!"
