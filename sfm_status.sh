#!/bin/bash
# SFM Status - Универсальная проверка статуса SFM
# Работает из любой директории

echo "🔍 Проверка статуса SFM..."

# Определяем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Переходим в директорию проекта
cd "$SCRIPT_DIR"

# Запускаем универсальный скрипт
python3 sfm_stats_universal.py

# Если не сработало, пробуем из других мест
if [ $? -ne 0 ]; then
    echo "Пробуем альтернативные пути..."
    
    # Пробуем из scripts/
    if [ -f "scripts/sfm_quick_stats.py" ]; then
        python3 scripts/sfm_quick_stats.py
    elif [ -f "scripts/sfm_analyzer.py" ]; then
        python3 scripts/sfm_analyzer.py
    else
        echo "❌ SFM скрипты не найдены!"
        echo "Искал в:"
        echo "  - $SCRIPT_DIR/sfm_stats_universal.py"
        echo "  - $SCRIPT_DIR/scripts/sfm_quick_stats.py"
        echo "  - $SCRIPT_DIR/scripts/sfm_analyzer.py"
    fi
fi