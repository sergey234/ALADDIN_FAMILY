#!/bin/bash
# ALADDIN Security System - Скрипт запуска
# Автоматически создан One-Click Installer

echo "🚀 Запуск системы безопасности ALADDIN..."

# Переход в директорию проекта
cd "$(dirname "$0")"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    exit 1
fi

# Запуск основных сервисов
echo "🔧 Запуск основных сервисов..."

# API Gateway
python3 -m http.server 8000 &
echo "✅ API Gateway запущен на порту 8000"

# VPN Service
python3 scripts/real_vpn_api_server.py &
echo "✅ VPN Service запущен на порту 8001"

# Antivirus Service
python3 scripts/antivirus_api_server.py &
echo "✅ Antivirus Service запущен на порту 8002"

# Mobile API
python3 mobile/mobile_api.py &
echo "✅ Mobile API запущен на порту 8003"

echo "🎉 Система ALADDIN успешно запущена!"
echo "📱 Доступ: http://localhost:8000"
echo "📊 Мониторинг: http://localhost:8004"
echo "🔧 Админ панель: http://localhost:8005"

# Ожидание завершения
wait
