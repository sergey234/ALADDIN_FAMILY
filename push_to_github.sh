#!/bin/bash
# 🚀 Скрипт для автоматического push в GitHub
# Использует expect для автоматизации аутентификации

set -e

echo "🚀 НАЧАЛО PUSH В GITHUB"
echo "================================"

# Переход в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Проверка что есть коммиты для пуша
COMMITS_TO_PUSH=$(git log --oneline origin/master..HEAD 2>/dev/null | wc -l | tr -d ' ')

if [ "$COMMITS_TO_PUSH" -eq "0" ]; then
    echo "⚠️ Нет коммитов для пуша"
    exit 0
fi

echo "📋 Коммитов для пуша: $COMMITS_TO_PUSH"
echo ""

# Показываем какие коммиты будут отправлены
echo "📤 Коммиты для отправки:"
git log --oneline origin/master..HEAD
echo ""

# Используем expect для автоматизации git push с force-with-lease
expect <<EOF
set timeout 300
spawn git push origin master --force-with-lease
expect {
    "Username for 'https://github.com':" {
        send "sergey234\r"
        exp_continue
    }
    "Password for 'https://sergey234@github.com':" {
        # Если нужен пароль, попробуем использовать credential helper
        send "\r"
        exp_continue
    }
    "Enter passphrase for key" {
        # Если SSH ключ защищен паролем
        send "\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    "Permission denied" {
        puts "\n❌ Ошибка аутентификации"
        exit 1
    }
    "Everything up-to-date" {
        puts "\n✅ Все уже отправлено"
        exit 0
    }
    "To https://github.com" {
        puts "\n✅ Push выполнен успешно!"
        exit 0
    }
    "To git@github.com" {
        puts "\n✅ Push выполнен успешно!"
        exit 0
    }
    eof
}
EOF

echo ""
echo "✅ ГОТОВО!"
