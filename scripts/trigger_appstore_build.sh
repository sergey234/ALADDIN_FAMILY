#!/bin/bash

# Скрипт для запуска сборки App Store через GitHub API
# Использование: ./scripts/trigger_appstore_build.sh

set -e

REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW_FILE="appstore.yml"
BRANCH="master"

echo "🚀 Запуск сборки App Store с подписью..."
echo ""

# Проверяем наличие GitHub токена
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN не установлен!"
    echo ""
    echo "Для автоматического запуска через API нужен GitHub Personal Access Token:"
    echo "1. Создайте токен: https://github.com/settings/tokens"
    echo "2. Права: repo, workflow"
    echo "3. Установите: export GITHUB_TOKEN=your_token"
    echo ""
    echo "Или запустите вручную через браузер:"
    echo "https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml"
    echo ""
    exit 1
fi

echo "✅ GitHub токен найден"
echo ""

# Запускаем workflow через API
echo "📤 Отправка запроса на запуск workflow..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW_FILE/dispatches" \
  -d "{\"ref\":\"$BRANCH\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 204 ]; then
    echo "✅ Workflow успешно запущен!"
    echo ""
    echo "📋 Следите за прогрессом:"
    echo "https://github.com/$REPO/actions/workflows/$WORKFLOW_FILE"
    echo ""
    echo "⏱️  Время выполнения: 20-30 минут"
else
    echo "❌ Ошибка при запуске workflow"
    echo "HTTP Code: $HTTP_CODE"
    echo "Response: $BODY"
    echo ""
    echo "Попробуйте запустить вручную:"
    echo "https://github.com/$REPO/actions/workflows/$WORKFLOW_FILE"
    exit 1
fi

