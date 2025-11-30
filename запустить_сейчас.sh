#!/bin/bash
# Быстрый запуск workflow appstore.yml

set -e

REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW_ID="210961430"  # ID workflow appstore.yml
BRANCH="master"

echo "🚀 Запуск workflow appstore.yml..."
echo ""

# Проверка токена
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Для запуска нужен GitHub Personal Access Token"
    echo ""
    echo "Быстрое получение токена:"
    echo "1. Откройте: https://github.com/settings/tokens/new"
    echo "2. Название: 'Workflow Trigger'"
    echo "3. Выберите: repo, workflow"
    echo "4. Нажмите 'Generate token'"
    echo "5. Скопируйте токен"
    echo ""
    read -sp "Введите токен: " GITHUB_TOKEN
    echo ""
    echo ""
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Токен не введен"
    exit 1
fi

echo "🚀 Запуск workflow..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW_ID/dispatches" \
    -d "{\"ref\":\"$BRANCH\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Workflow успешно запущен!"
    echo ""
    echo "🔗 Проверьте статус:"
    echo "https://github.com/$REPO/actions"
    echo ""
    echo "Workflow: Build and Upload to App Store"
else
    echo "❌ Ошибка при запуске (HTTP $HTTP_CODE)"
    echo "Проверьте токен и права доступа"
    exit 1
fi

