#!/bin/bash
# Простой скрипт для проверки статуса workflow

GITHUB_TOKEN="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"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="appstore.yml"

echo "📊 Статус последних запусков workflow:"
echo ""

curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?per_page=5" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
total = data.get('total_count', 0)
print(f'Всего запусков: {total}')
print('')
for i, run in enumerate(runs, 1):
    status = run.get('status', 'unknown')
    conclusion = run.get('conclusion', '')
    run_num = run.get('run_number', '?')
    title = run.get('display_title', '')[:60]
    url = run.get('html_url', '')
    
    if status == 'completed':
        icon = '✅' if conclusion == 'success' else '❌'
    elif status == 'in_progress':
        icon = '🟡'
    elif status == 'queued':
        icon = '⏳'
    else:
        icon = '⚪'
    
    print(f'{icon} #{run_num}: {title}')
    print(f'   Статус: {status}' + (f', Результат: {conclusion}' if conclusion else ''))
    print(f'   {url}')
    print('')
"

