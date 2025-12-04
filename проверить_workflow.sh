#!/bin/bash
# Скрипт для детальной проверки статуса workflow

GITHUB_TOKEN="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"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="appstore.yml"

echo "🔍 ДИАГНОСТИКА WORKFLOW"
echo "======================"
echo ""

# 1. Проверка последних запусков
echo "📊 Последние 5 запусков:"
echo ""

response=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?per_page=5")

# Сохраняем ответ для отладки
echo "$response" > /tmp/workflow_runs.json 2>/dev/null

if [ -z "$response" ] || [ "$response" = "null" ]; then
    echo "❌ Пустой ответ от API"
    echo "   Проверьте токен и права доступа"
else
    echo "$response" | python3 << 'PYEOF'
import sys, json
from datetime import datetime

try:
    data = json.load(sys.stdin)
    runs = data.get('workflow_runs', [])
    
    if not runs:
        print("❌ Запуски не найдены")
    else:
        for i, run in enumerate(runs, 1):
            status = run.get('status', 'unknown')
            conclusion = run.get('conclusion', 'в процессе')
            created = run.get('created_at', '')
            run_id = run.get('id', '')
            html_url = run.get('html_url', '')
            
            # Иконка статуса
            if status == 'completed':
                if conclusion == 'success':
                    icon = "✅"
                elif conclusion == 'failure':
                    icon = "❌"
                else:
                    icon = "⚠️"
            elif status == 'in_progress':
                icon = "🟡"
            elif status == 'queued':
                icon = "⏳"
            else:
                icon = "⚪"
            
            print(f"{icon} Запуск #{i} (ID: {run_id})")
            print(f"   Статус: {status}")
            print(f"   Результат: {conclusion}")
            print(f"   Создан: {created}")
            print(f"   Ссылка: {html_url}")
            print("")
            
            if i == 1:
                print("   👆 Это последний запуск")
                print("")
except Exception as e:
    print(f"❌ Ошибка парсинга: {e}")
    print(f"   Ответ API (первые 200 символов):")
    import sys
    sys.stdin.seek(0)
    content = sys.stdin.read()
    print(f"   {content[:200]}")
PYEOF
fi

echo ""
echo "======================"
echo ""

# 2. Проверка workflow файла
echo "📄 Проверка workflow файла:"
echo ""

file_response=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/contents/.github/workflows/$WORKFLOW")

echo "$file_response" | python3 << 'PYEOF'
import sys, json

try:
    data = json.load(sys.stdin)
    if 'message' in data:
        print(f"❌ Ошибка: {data['message']}")
    else:
        print(f"✅ Файл существует")
        print(f"   Размер: {data.get('size', 0)} байт")
        print(f"   SHA: {data.get('sha', '')[:10]}...")
except Exception as e:
    print(f"❌ Ошибка: {e}")
PYEOF

echo ""
echo "======================"
echo ""

# 3. Попытка запуска workflow
echo "🚀 Попытка запуска workflow..."
echo ""

run_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d '{"ref":"master"}')

http_code=$(echo "$run_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$run_response" | grep -v "HTTP_CODE")

if [ "$http_code" = "204" ]; then
    echo "✅ Workflow успешно запущен! (HTTP 204)"
    echo ""
    echo "Подождите 5 секунд и проверьте статус..."
    sleep 5
    
    # Проверяем новый запуск
    echo ""
    echo "📊 Проверка нового запуска:"
    new_response=$(curl -s -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: token $GITHUB_TOKEN" \
      "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?per_page=1")
    
    echo "$new_response" | python3 << 'PYEOF'
import sys, json
from datetime import datetime

try:
    data = json.load(sys.stdin)
    runs = data.get('workflow_runs', [])
    
    if runs:
        run = runs[0]
        print(f"   ID: {run.get('id', '')}")
        print(f"   Статус: {run.get('status', 'unknown')}")
        print(f"   Создан: {run.get('created_at', '')}")
        print(f"   Ссылка: {run.get('html_url', '')}")
        
        status = run.get('status', '')
        if status == 'queued':
            print("   ⏳ Workflow в очереди на выполнение")
        elif status == 'in_progress':
            print("   🟡 Workflow выполняется")
        elif status == 'completed':
            conclusion = run.get('conclusion', '')
            if conclusion == 'success':
                print("   ✅ Workflow успешно завершен!")
            else:
                print(f"   ❌ Workflow завершился: {conclusion}")
    else:
        print("   ⚠️ Новый запуск еще не появился (подождите еще немного)")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
PYEOF
else
    echo "❌ Ошибка при запуске workflow (HTTP $http_code)"
    echo ""
    echo "Ответ сервера:"
    echo "$body"
    echo ""
    
    if [ "$http_code" = "404" ]; then
        echo "💡 Возможные причины:"
        echo "   - Workflow файл не найден"
        echo "   - Неправильное имя workflow"
        echo "   - Нет прав доступа"
    elif [ "$http_code" = "401" ]; then
        echo "💡 Возможные причины:"
        echo "   - Неверный токен"
        echo "   - Токен истек"
        echo "   - Нет прав workflow"
    elif [ "$http_code" = "422" ]; then
        echo "💡 Возможные причины:"
        echo "   - Workflow отключен"
        echo "   - Ошибка в workflow файле"
        echo "   - Неправильная ветка"
    fi
fi

echo ""
echo "======================"
echo ""
echo "📋 ПРЯМЫЕ ССЫЛКИ:"
echo "   Workflow: https://github.com/$REPO/actions/workflows/$WORKFLOW"
echo "   Все Actions: https://github.com/$REPO/actions"
echo ""

