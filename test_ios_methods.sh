#!/bin/bash

# 🚀 Скрипт для тестирования всех iOS методов
# Цель: Протестировать все методы в APIService.swift

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Тестирование iOS методов через Xcode"
echo ""

# Проверяем наличие Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}❌ Xcode не найден${NC}"
    echo "Установите Xcode для запуска тестов"
    exit 1
fi

# Запускаем Unit тесты
echo "📱 Запуск Unit тестов..."
xcodebuild test \
    -project ALADDIN.xcodeproj \
    -scheme ALADDIN \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    -only-testing:ALADDINTests \
    2>&1 | tee test_unit_results.log

# Запускаем Integration тесты
echo ""
echo "🔗 Запуск Integration тестов..."
xcodebuild test \
    -project ALADDIN.xcodeproj \
    -scheme ALADDIN \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    -only-testing:ALADDINIntegrationTests \
    2>&1 | tee test_integration_results.log

# Запускаем UI тесты
echo ""
echo "🎨 Запуск UI тестов..."
xcodebuild test \
    -project ALADDIN.xcodeproj \
    -scheme ALADDIN \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    -only-testing:ALADDINUITests \
    2>&1 | tee test_ui_results.log

echo ""
echo "✅ Тестирование завершено!"
echo "📄 Результаты сохранены в:"
echo "   - test_unit_results.log"
echo "   - test_integration_results.log"
echo "   - test_ui_results.log"
