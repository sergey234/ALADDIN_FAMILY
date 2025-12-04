#!/bin/bash
# Скрипт для запуска workflow через GitHub API

REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW_FILE="appstore.yml"
BRANCH="master"

echo "🚀 Запуск workflow через GitHub API..."
echo ""

# Проверка наличия GitHub CLI
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI найден, используем его..."
    gh workflow run "$WORKFLOW_FILE" --ref "$BRANCH"
    if [ $? -eq 0 ]; then
        echo "✅ Workflow запущен через GitHub CLI!"
        echo ""
        echo "Проверьте статус:"
        echo "https://github.com/$REPO/actions/workflows/$WORKFLOW_FILE"
    else
        echo "❌ Ошибка при запуске через GitHub CLI"
        echo "Убедитесь, что вы авторизованы: gh auth login"
    fi
else
    echo "⚠️  GitHub CLI не установлен"
    echo ""
    echo "Для запуска через API нужен токен доступа."
    echo ""
    echo "Варианты:"
    echo "1. Установите GitHub CLI: brew install gh"
    echo "2. Авторизуйтесь: gh auth login"
    echo "3. Запустите: gh workflow run appstore.yml --ref master"
    echo ""
    echo "Или запустите вручную через GitHub UI:"
    echo "https://github.com/$REPO/actions/workflows/$WORKFLOW_FILE"
fi
