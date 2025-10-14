#!/bin/bash
# ALADDIN Security System - Деинсталлятор
# Автоматически создан One-Click Installer

echo "🗑️ Удаление системы безопасности ALADDIN..."

# Остановка всех процессов ALADDIN
echo "⏹️ Остановка сервисов..."
pkill -f "aladdin"
pkill -f "vpn"
pkill -f "antivirus"

# Удаление файлов (с подтверждением)
read -p "Удалить все файлы ALADDIN? (y/N): " confirm
if [[ $confirm == [yY] ]]; then
    echo "🗑️ Удаление файлов..."
    rm -rf logs/
    rm -rf data/
    rm -rf backups/
    rm -rf config/
    echo "✅ Файлы удалены"
else
    echo "ℹ️ Файлы сохранены"
fi

echo "✅ Деинсталляция завершена"
