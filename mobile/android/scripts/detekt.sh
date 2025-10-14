#!/bin/bash

# Detekt скрипт для ALADDIN Mobile Android
# Автоматическая проверка и исправление кода

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Detekt проверка для ALADDIN Mobile Android${NC}"
echo "================================================"

# Переход в директорию Android проекта
cd "$(dirname "$0")/.."

# Проверка наличия Gradle wrapper
if [ ! -f "gradlew" ]; then
    echo -e "${RED}❌ Gradle wrapper не найден${NC}"
    echo "Убедитесь, что вы находитесь в директории Android проекта"
    exit 1
fi

# Проверка наличия конфигурации Detekt
if [ ! -f "config/detekt.yml" ]; then
    echo -e "${YELLOW}⚠️  Конфигурация detekt.yml не найдена${NC}"
    echo "Создаю базовую конфигурацию..."
    ./gradlew detektGenerateConfig
fi

echo -e "${BLUE}📋 Запуск Detekt проверки...${NC}"

# Запуск проверки
if ./gradlew detekt --quiet; then
    echo -e "${GREEN}✅ Detekt проверка пройдена успешно!${NC}"
else
    echo -e "${RED}❌ Detekt нашел проблемы в коде${NC}"
    echo ""
    echo "Для подробного отчета:"
    echo "  ./gradlew detekt"
    echo ""
    echo "Для HTML отчета:"
    echo "  ./gradlew detekt --reports html"
    exit 1
fi

echo -e "${BLUE}📋 Запуск ktlint проверки...${NC}"

# Проверка ktlint
if command -v ktlint &> /dev/null; then
    if ktlint check; then
        echo -e "${GREEN}✅ ktlint проверка пройдена успешно!${NC}"
        
        # Предложение автоисправления
        echo -e "${BLUE}🔧 Запуск автоисправления ktlint...${NC}"
        if ktlint format; then
            echo -e "${GREEN}✅ ktlint автоисправление завершено!${NC}"
        else
            echo -e "${YELLOW}⚠️  Некоторые проблемы ktlint не удалось исправить автоматически${NC}"
        fi
    else
        echo -e "${RED}❌ ktlint нашел проблемы в коде${NC}"
        echo ""
        echo "Для исправления запустите:"
        echo "  ktlint format"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  ktlint не установлен. Установите: brew install ktlint${NC}"
fi

echo -e "${BLUE}📋 Запуск Android Lint проверки...${NC}"

# Запуск Android Lint
if ./gradlew lint --quiet; then
    echo -e "${GREEN}✅ Android Lint проверка пройдена успешно!${NC}"
else
    echo -e "${YELLOW}⚠️  Android Lint нашел проблемы${NC}"
    echo "Для подробного отчета:"
    echo "  ./gradlew lint"
    echo "Отчет будет в app/build/reports/lint-results.html"
fi

echo -e "${GREEN}🎉 Проверка завершена!${NC}"

