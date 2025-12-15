#!/bin/bash

# Скрипт для автоматического запуска workflow "Upload IPA to App Store Connect"
# Использует GitHub API для запуска workflow_dispatch

set -e

# Конфигурация
REPO_OWNER="sergey234"
REPO_NAME="ALADDIN_FAMILY"
WORKFLOW_FILE="upload-ipa-only.yml"
BRANCH="main"
ARTIFACT_NAME="ALADDIN-IPA"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Запуск workflow для загрузки IPA в App Store Connect${NC}"
echo ""

# Проверка наличия токена
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN не найден в переменных окружения${NC}"
    echo ""
    echo "Для запуска workflow нужен GitHub Personal Access Token."
    echo ""
    echo "Создайте токен:"
    echo "1. Перейдите: https://github.com/settings/tokens"
    echo "2. Нажмите 'Generate new token (classic)'"
    echo "3. Выберите scope: 'repo' (полный доступ к репозиторию)"
    echo "4. Скопируйте токен"
    echo ""
    echo "Затем запустите:"
    echo "  export GITHUB_TOKEN=ваш_токен"
    echo "  ./scripts/trigger_upload_workflow.sh"
    echo ""
    exit 1
fi

# Получаем workflow ID
echo "📋 Получение информации о workflow..."
WORKFLOW_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows")

WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$WORKFLOW_ID" ]; then
    # Пробуем найти по имени файла
    WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | grep -B5 "$WORKFLOW_FILE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
fi

if [ -z "$WORKFLOW_ID" ]; then
    echo -e "${RED}❌ Не удалось найти workflow '$WORKFLOW_FILE'${NC}"
    echo ""
    echo "Доступные workflows:"
    echo "$WORKFLOW_RESPONSE" | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g'
    exit 1
fi

echo -e "${GREEN}✅ Workflow найден (ID: $WORKFLOW_ID)${NC}"
echo ""

# Запускаем workflow
echo "🚀 Запуск workflow..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows/$WORKFLOW_ID/dispatches" \
    -d "{
        \"ref\": \"$BRANCH\",
        \"inputs\": {
            \"artifact_name\": \"$ARTIFACT_NAME\",
            \"run_id\": \"\"
        }
    }")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "204" ]; then
    echo -e "${GREEN}✅ Workflow успешно запущен!${NC}"
    echo ""
    echo "📊 Отслеживание выполнения:"
    echo "   https://github.com/$REPO_OWNER/$REPO_NAME/actions"
    echo ""
    echo "⏳ Workflow выполняется (~5-10 минут)"
    echo "   После завершения билд появится в App Store Connect → TestFlight → Builds"
    exit 0
else
    echo -e "${RED}❌ Ошибка при запуске workflow${NC}"
    echo "HTTP Code: $HTTP_CODE"
    echo "Response: $BODY"
    exit 1
fi

