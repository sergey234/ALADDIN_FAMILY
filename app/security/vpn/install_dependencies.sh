#!/bin/bash

# ALADDIN VPN Server Installation Script
# Установка зависимостей для VPN сервера

echo "🚀 Установка зависимостей ALADDIN VPN Server..."
echo "================================================"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден! Установите Python 3.8+"
    exit 1
fi

echo "✅ Python3 найден: $(python3 --version)"

# Проверяем pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден! Установите pip"
    exit 1
fi

echo "✅ pip3 найден: $(pip3 --version)"

# Создаем виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

echo ""
echo "✅ Установка завершена!"
echo "================================================"
echo "Для запуска сервера выполните:"
echo "  source venv/bin/activate"
echo "  python start_vpn_server.py"
echo "================================================"


