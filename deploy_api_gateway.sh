#!/bin/bash
# 🚀 РАЗВЕРТЫВАНИЕ API GATEWAY - ОБЕРТКА

echo "=========================================="
echo "🚀 РАЗВЕРТЫВАНИЕ API GATEWAY"
echo "=========================================="
echo ""

# Проверка наличия expect
if ! command -v expect &> /dev/null; then
    echo "❌ expect не установлен!"
    echo "   Установите: brew install expect (macOS)"
    exit 1
fi

# ШАГ 1: Создание backup
echo "🛡️ ШАГ 1: Создание backup..."
./create_backup_before_deploy.exp

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при создании backup!"
    exit 1
fi

echo ""
echo "✅ Backup создан!"
echo ""

# ШАГ 2: Развертывание
echo "🚀 ШАГ 2: Развертывание API Gateway..."
./deploy_api_gateway_final.exp

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при развертывании!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="



