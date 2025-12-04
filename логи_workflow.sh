#!/bin/bash
# Простой скрипт для проверки логов workflow

GITHUB_TOKEN="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"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="appstore.yml"

echo "🔍 ДИАГНОСТИКА WORKFLOW"
echo "======================"
echo ""

# 1. Запуск workflow
echo "🚀 Запуск workflow..."
response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d '{"ref":"master"}')

http_code=$(echo "$response" | tail -1)

if [ "$http_code" = "204" ]; then
    echo "✅ Workflow запущен! (HTTP 204)"
    echo ""
    echo "⏳ Ожидание появления нового запуска (10 секунд)..."
    sleep 10
else
    echo "❌ Ошибка запуска (HTTP $http_code)"
    exit 1
fi

# 2. Проверка последнего запуска
echo ""
echo "📊 Последний запуск:"
echo ""

run_data=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?per_page=1")

# Извлекаем ID и URL
run_id=$(echo "$run_data" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
run_url=$(echo "$run_data" | grep -o '"html_url":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$run_id" ]; then
    echo "   ID: $run_id"
    echo "   Ссылка: $run_url"
    echo ""
    
    # Получаем статус
    status=$(echo "$run_data" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
    conclusion=$(echo "$run_data" | grep -o '"conclusion":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    echo "   Статус: $status"
    if [ -n "$conclusion" ]; then
        echo "   Результат: $conclusion"
    fi
    echo ""
    
    if [ "$status" = "in_progress" ]; then
        echo "   🟡 Workflow выполняется..."
    elif [ "$status" = "queued" ]; then
        echo "   ⏳ Workflow в очереди..."
    elif [ "$conclusion" = "failure" ]; then
        echo "   ❌ Workflow завершился с ошибкой"
        echo ""
        echo "   💡 Откройте ссылку выше, чтобы увидеть детальные логи:"
        echo "   $run_url"
    elif [ "$conclusion" = "success" ]; then
        echo "   ✅ Workflow успешно завершен!"
    fi
else
    echo "   ⚠️  Не удалось получить информацию о запуске"
fi

echo ""
echo "======================"
echo ""
echo "📋 ПРЯМЫЕ ССЫЛКИ:"
echo "   Workflow: https://github.com/$REPO/actions/workflows/$WORKFLOW"
echo "   Все Actions: https://github.com/$REPO/actions"
echo ""

