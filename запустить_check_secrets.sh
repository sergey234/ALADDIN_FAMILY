#!/bin/bash
# Скрипт для запуска check-secrets.yml через GitHub API

# Токен должен быть установлен как переменная окружения или в отдельном файле
# export GITHUB_TOKEN="your_token_here"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="check-secrets.yml"
BRANCH="master"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Ошибка: GITHUB_TOKEN не установлен!"
    echo ""
    echo "Установите токен:"
    echo "  export GITHUB_TOKEN=\"your_token_here\""
    echo "  bash запустить_check_secrets.sh"
    exit 1
fi

echo "🚀 Запуск workflow check-secrets.yml через GitHub API..."
echo ""

response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d "{\"ref\":\"$BRANCH\"}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "204" ]; then
    echo "✅ Workflow check-secrets.yml успешно запущен!"
    echo ""
    echo "🔗 Проверьте статус:"
    echo "https://github.com/$REPO/actions/workflows/$WORKFLOW"
else
    echo "❌ Ошибка при запуске workflow (HTTP $http_code)"
    echo "$body"
    exit 1
fi

