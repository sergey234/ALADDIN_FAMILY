#!/bin/bash
# Скрипт для запуска workflow appstore.yml через GitHub API

set -e

REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW_FILE="appstore.yml"
BRANCH="master"

echo "🚀 Запуск workflow appstore.yml через GitHub API..."
echo ""

# Проверка наличия токена
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Ошибка: GITHUB_TOKEN не установлен!"
    echo ""
    echo "Для запуска workflow нужен GitHub Personal Access Token."
    echo ""
    echo "Инструкция:"
    echo "1. Откройте: https://github.com/settings/tokens"
    echo "2. Нажмите 'Generate new token (classic)'"
    echo "3. Выберите права:"
    echo "   - repo (полный доступ к репозиторию)"
    echo "   - workflow (управление GitHub Actions)"
    echo "4. Скопируйте токен"
    echo "5. Запустите команду:"
    echo "   export GITHUB_TOKEN=ваш_токен"
    echo "   ./запустить_workflow.sh"
    echo ""
    echo "Или введите токен сейчас (он не будет сохранен):"
    read -s GITHUB_TOKEN
    export GITHUB_TOKEN
    echo ""
fi

# Получить workflow ID
echo "📋 Получение ID workflow..."
WORKFLOW_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/actions/workflows")

WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$WORKFLOW_ID" ]; then
    # Попробовать найти по имени файла
    echo "Попытка найти workflow по имени файла..."
    WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | grep -A 5 "$WORKFLOW_FILE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
fi

if [ -z "$WORKFLOW_ID" ]; then
    echo "❌ Не удалось найти workflow ID"
    echo "Ответ API:"
    echo "$WORKFLOW_RESPONSE" | head -20
    exit 1
fi

echo "✅ Workflow ID найден: $WORKFLOW_ID"
echo ""

# Запустить workflow
echo "🚀 Запуск workflow..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW_ID/dispatches" \
    -d "{\"ref\":\"$BRANCH\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Workflow успешно запущен!"
    echo ""
    echo "🔗 Проверьте статус:"
    echo "https://github.com/$REPO/actions"
    echo ""
    echo "Workflow: Build and Upload to App Store"
else
    echo "❌ Ошибка при запуске workflow"
    echo "HTTP код: $HTTP_CODE"
    echo "Ответ: $BODY"
    exit 1
fi

