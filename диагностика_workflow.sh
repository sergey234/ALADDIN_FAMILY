#!/bin/bash
# Улучшенный скрипт диагностики workflow

GITHUB_TOKEN="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"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="appstore.yml"

echo "🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА WORKFLOW"
echo "=================================="
echo ""

# 1. Проверка последних запусков
echo "📊 Последние 5 запусков workflow:"
echo ""

response=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?per_page=5")

if [ $? -ne 0 ]; then
    echo "❌ Ошибка подключения к GitHub API"
    exit 1
fi

echo "$response" | python3 << 'PYEOF'
import sys, json
from datetime import datetime

try:
    data = json.load(sys.stdin)
    
    if 'message' in data:
        print(f"❌ Ошибка API: {data['message']}")
        sys.exit(1)
    
    total = data.get('total_count', 0)
    runs = data.get('workflow_runs', [])
    
    print(f"Всего запусков: {total}")
    print("")
    
    if not runs:
        print("❌ Запуски не найдены")
    else:
        for i, run in enumerate(runs, 1):
            status = run.get('status', 'unknown')
            conclusion = run.get('conclusion')
            created = run.get('created_at', '')
            run_id = run.get('id', '')
            run_number = run.get('run_number', '')
            html_url = run.get('html_url', '')
            event = run.get('event', '')
            head_branch = run.get('head_branch', '')
            display_title = run.get('display_title', '')
            
            # Иконка статуса
            if status == 'completed':
                if conclusion == 'success':
                    icon = "✅"
                elif conclusion == 'failure':
                    icon = "❌"
                elif conclusion == 'cancelled':
                    icon = "🚫"
                else:
                    icon = "⚠️"
            elif status == 'in_progress':
                icon = "🟡"
            elif status == 'queued':
                icon = "⏳"
            else:
                icon = "⚪"
            
            print(f"{icon} Запуск #{run_number} (ID: {run_id})")
            print(f"   Название: {display_title}")
            print(f"   Статус: {status}")
            if conclusion:
                print(f"   Результат: {conclusion}")
            print(f"   Событие: {event}")
            print(f"   Ветка: {head_branch}")
            print(f"   Создан: {created}")
            print(f"   Ссылка: {html_url}")
            print("")
            
            if i == 1:
                print("   👆 Это последний запуск")
                print("")
                
                # Детали последнего запуска
                if status == 'completed' and conclusion == 'failure':
                    print("   ⚠️  Последний запуск завершился с ошибкой")
                    print("   💡 Откройте ссылку выше, чтобы увидеть детали ошибки")
                elif status == 'in_progress':
                    print("   🟡 Workflow выполняется прямо сейчас!")
                elif status == 'queued':
                    print("   ⏳ Workflow в очереди на выполнение")
except json.JSONDecodeError as e:
    print(f"❌ Ошибка парсинга JSON: {e}")
    print(f"   Ответ API (первые 500 символов):")
    sys.stdin.seek(0)
    content = sys.stdin.read()
    print(f"   {content[:500]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
PYEOF

echo ""
echo "=================================="
echo ""

# 2. Попытка запуска нового workflow
echo "🚀 Запуск нового workflow..."
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
    echo "⏳ Подождите 5 секунд для появления нового запуска..."
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
        run_id = run.get('id', '')
        status = run.get('status', 'unknown')
        created = run.get('created_at', '')
        html_url = run.get('html_url', '')
        
        print(f"   ✅ Новый запуск найден!")
        print(f"   ID: {run_id}")
        print(f"   Статус: {status}")
        print(f"   Создан: {created}")
        print(f"   Ссылка: {html_url}")
        print("")
        
        if status == 'queued':
            print("   ⏳ Workflow в очереди на выполнение")
        elif status == 'in_progress':
            print("   🟡 Workflow выполняется прямо сейчас!")
        elif status == 'completed':
            conclusion = run.get('conclusion', '')
            if conclusion == 'success':
                print("   ✅ Workflow успешно завершен!")
            else:
                print(f"   ❌ Workflow завершился: {conclusion}")
    else:
        print("   ⚠️  Новый запуск еще не появился")
        print("   💡 Подождите еще 10-20 секунд и проверьте вручную")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
PYEOF
else
    echo "❌ Ошибка при запуске workflow (HTTP $http_code)"
    echo ""
    if [ -n "$body" ]; then
        echo "Ответ сервера:"
        echo "$body"
        echo ""
    fi
    
    case "$http_code" in
        404)
            echo "💡 Возможные причины:"
            echo "   - Workflow файл не найден"
            echo "   - Неправильное имя workflow"
            echo "   - Нет прав доступа к репозиторию"
            ;;
        401)
            echo "💡 Возможные причины:"
            echo "   - Неверный или истекший токен"
            echo "   - Токен не имеет прав 'workflow'"
            echo "   - Проверьте токен: https://github.com/settings/tokens"
            ;;
        422)
            echo "💡 Возможные причины:"
            echo "   - Workflow отключен в настройках"
            echo "   - Ошибка в workflow файле"
            echo "   - Неправильная ветка (master не существует)"
            ;;
        *)
            echo "💡 Неизвестная ошибка HTTP $http_code"
            ;;
    esac
fi

echo ""
echo "=================================="
echo ""
echo "📋 ПРЯМЫЕ ССЫЛКИ:"
echo "   Workflow: https://github.com/$REPO/actions/workflows/$WORKFLOW"
echo "   Все Actions: https://github.com/$REPO/actions"
echo ""
echo "💡 СОВЕТ: Если workflow не запускается, проверьте:"
echo "   1. Настройки Actions включены?"
echo "   2. Workflow файл существует и валиден?"
echo "   3. Токен имеет права 'workflow'?"
echo ""

