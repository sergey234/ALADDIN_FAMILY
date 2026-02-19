#!/bin/bash

# Скрипт для тестирования runtime поведения ALADDIN в симуляторе
# Запускает приложение и проверяет логи на зависание

echo "🔬 Тестирование runtime поведения ALADDIN..."
echo ""

# Проверяем, что xcrun доступен
if ! command -v xcrun &> /dev/null; then
    echo "❌ xcrun не найден"
    exit 1
fi

# Переходим в директорию проекта
cd "$(dirname "$0")" || exit 1

echo "📱 Запуск симулятора..."
xcrun simctl boot "iPhone 13" 2>/dev/null || echo "Симулятор уже запущен"

echo "🚀 Установка и запуск приложения..."
xcrun simctl install booted "Build/Products/Debug-iphonesimulator/ALADDIN.app" 2>/dev/null || echo "Приложение уже установлено"

echo "📊 Запуск приложения..."
xcrun simctl launch booted "ALADDIN.ALADDIN" &

# Ждем 10 секунд для инициализации
sleep 10

echo "🔍 Проверка логов симулятора..."
xcrun simctl spawn booted log stream --level debug --predicate 'process == "ALADDIN"' --timeout 5 | head -20

echo ""
echo "✅ Тест завершен. Проверьте логи выше на наличие зависания."