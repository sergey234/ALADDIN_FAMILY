#!/bin/bash
# -*- coding: utf-8 -*-
"""
Setup Log Rotation Cron - Настройка автоматической ротации логов
Скрипт для настройки еженедельной ротации логов через cron
"""

echo "🚀 Настройка автоматической ротации логов ALADDIN"
echo "=================================================="

# Получаем текущую директорию
CURRENT_DIR=$(pwd)
SCRIPT_PATH="$CURRENT_DIR/scripts/log_rotation_manager.py"

# Проверяем существование скрипта
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Скрипт ротации логов не найден: $SCRIPT_PATH"
    exit 1
fi

echo "📁 Директория проекта: $CURRENT_DIR"
echo "📄 Скрипт ротации: $SCRIPT_PATH"

# Создаем cron задачу
CRON_JOB="0 2 * * 0 cd $CURRENT_DIR && python3 $SCRIPT_PATH >> logs/rotation.log 2>&1"

echo "⏰ Cron задача: $CRON_JOB"

# Добавляем задачу в crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Автоматическая ротация логов настроена успешно!"
    echo "📅 Ротация будет выполняться каждое воскресенье в 02:00"
    echo "📄 Логи ротации сохраняются в: logs/rotation.log"
    
    # Показываем текущие cron задачи
    echo ""
    echo "📋 Текущие cron задачи:"
    crontab -l | grep -E "(log_rotation|ALADDIN)" || echo "   (задачи ALADDIN не найдены)"
    
else
    echo "❌ Ошибка настройки cron задачи"
    exit 1
fi

echo ""
echo "🔧 Для проверки ротации вручную выполните:"
echo "   python3 $SCRIPT_PATH"
echo ""
echo "📊 Для мониторинга логов ротации:"
echo "   tail -f logs/rotation.log"