#!/bin/bash

# 🚀 ЗАПУСК ПРОВЕРКИ МИГРАЦИИ ГРУППЫ 3
# Использует expect для автоматизации

echo "🔍 ЗАПУСК АВТОМАТИЧЕСКОЙ ПРОВЕРКИ МИГРАЦИИ ГРУППЫ 3"
echo "=================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECT_SCRIPT="$SCRIPT_DIR/auto_check_group3.sh"

if [ -f "$EXPECT_SCRIPT" ]; then
    echo "✅ Скрипт найден: $EXPECT_SCRIPT"
    echo "🚀 Запуск проверки..."
    echo ""
    /usr/bin/expect -f "$EXPECT_SCRIPT"
else
    echo "❌ Скрипт не найден: $EXPECT_SCRIPT"
    exit 1
fi


