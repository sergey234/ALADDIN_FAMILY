#!/bin/bash
# Скрипт для проверки ошибок в последнем запуске workflow

GITHUB_TOKEN="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"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="appstore.yml"

echo "🔍 ПРОВЕРКА ОШИБОК В ПОСЛЕДНЕМ ЗАПУСКЕ"
echo "======================================"
echo ""

# Получаем последний запуск
run_data=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?per_page=1")

run_id=$(echo "$run_data" | python3 -c "import sys, json; data=json.load(sys.stdin); runs=data.get('workflow_runs',[]); print(runs[0]['id'] if runs else '')")

if [ -z "$run_id" ]; then
    echo "❌ Не удалось получить ID последнего запуска"
    exit 1
fi

echo "📊 Последний запуск: ID $run_id"
echo ""

# Получаем информацию о job'ах
jobs_data=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/runs/$run_id/jobs")

echo "$jobs_data" | python3 << 'PYEOF'
import sys, json

try:
    data = json.load(sys.stdin)
    jobs = data.get('jobs', [])
    
    if not jobs:
        print("❌ Jobs не найдены")
        sys.exit(1)
    
    for job in jobs:
        name = job.get('name', '')
        status = job.get('status', '')
        conclusion = job.get('conclusion', '')
        html_url = job.get('html_url', '')
        
        print(f"Job: {name}")
        print(f"  Статус: {status}")
        print(f"  Результат: {conclusion}")
        print(f"  Ссылка: {html_url}")
        print("")
        
        # Показываем шаги
        steps = job.get('steps', [])
        if steps:
            print("  Шаги:")
            for step in steps:
                step_name = step.get('name', '')
                step_status = step.get('status', '')
                step_conclusion = step.get('conclusion', '')
                
                if step_conclusion == 'failure' or (step_status == 'completed' and step_conclusion != 'success'):
                    icon = "❌"
                elif step_status == 'in_progress':
                    icon = "🟡"
                elif step_conclusion == 'success':
                    icon = "✅"
                else:
                    icon = "⚪"
                
                print(f"    {icon} {step_name}")
                print(f"       Статус: {step_status}, Результат: {step_conclusion or 'в процессе'}")
                
                if step_conclusion == 'failure':
                    print(f"       ⚠️  ОШИБКА В ЭТОМ ШАГЕ!")
            print("")
        
        if conclusion == 'failure':
            print("  💡 Откройте ссылку выше, чтобы увидеть детальные логи ошибки")
            print("")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
PYEOF

echo "======================================"
echo ""
echo "📋 Ссылка на последний запуск:"
echo "https://github.com/$REPO/actions/runs/$run_id"
echo ""

