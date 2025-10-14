#!/bin/bash

# SwiftLint скрипт для ALADDIN Mobile iOS
# Автоматическая проверка и исправление кода

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 SwiftLint проверка для ALADDIN Mobile iOS${NC}"
echo "=============================================="

# Проверка установки SwiftLint
if ! command -v swiftlint &> /dev/null; then
    echo -e "${RED}❌ SwiftLint не установлен${NC}"
    echo "Установите: brew install swiftlint"
    exit 1
fi

# Переход в директорию iOS проекта
cd "$(dirname "$0")/.."

# Проверка наличия конфигурации
if [ ! -f ".swiftlint.yml" ]; then
    echo -e "${YELLOW}⚠️  Конфигурация .swiftlint.yml не найдена${NC}"
    echo "Создаю базовую конфигурацию..."
    swiftlint config generate
fi

echo -e "${BLUE}📋 Запуск SwiftLint проверки...${NC}"

# Запуск проверки
if swiftlint lint --reporter emoji; then
    echo -e "${GREEN}✅ SwiftLint проверка пройдена успешно!${NC}"
    
    # Предложение автоисправления
    echo -e "${BLUE}🔧 Запуск автоисправления...${NC}"
    if swiftlint --fix; then
        echo -e "${GREEN}✅ Автоисправление завершено!${NC}"
    else
        echo -e "${YELLOW}⚠️  Некоторые проблемы не удалось исправить автоматически${NC}"
    fi
else
    echo -e "${RED}❌ SwiftLint нашел проблемы в коде${NC}"
    echo ""
    echo "Для исправления запустите:"
    echo "  swiftlint --fix"
    echo ""
    echo "Для подробного отчета:"
    echo "  swiftlint lint --reporter html > swiftlint-report.html"
    exit 1
fi

echo -e "${GREEN}🎉 Проверка завершена!${NC}"

