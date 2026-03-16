#!/bin/bash
# 🚀 Деплой исправления для /api/family/stats (BUILD 121)

set -e  # Остановка при ошибке

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend/app/auth"
LOCAL_FILE="app/auth/auth.py"
BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ 401 ДЛЯ /api/family/stats"
echo "=========================================="
echo ""

# Проверка наличия файла
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ Ошибка: Файл $LOCAL_FILE не найден!"
    exit 1
fi

echo "✅ Локальный файл найден: $LOCAL_FILE"
echo ""

# Загрузка файла на сервер через SCP
echo "📤 ШАГ 1: Загрузка файла на сервер..."
echo "   - Сервер: $USER@$SERVER"
echo "   - Путь: $REMOTE_PATH/auth.py"

# Используем sshpass для автоматической передачи пароля
if command -v sshpass &> /dev/null; then
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_FILE" "$USER@$SERVER:$REMOTE_PATH/auth.py"
else
    echo "⚠️ sshpass не установлен. Используйте ручную загрузку:"
    echo "   scp $LOCAL_FILE $USER@$SERVER:$REMOTE_PATH/auth.py"
    echo "   Пароль: $PASSWORD"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "✅ Файл успешно загружен!"
else
    echo "❌ Ошибка при загрузке файла!"
    exit 1
fi

echo ""

# Подключение к серверу и выполнение команд
echo "🔧 ШАГ 2: Резервное копирование и перезапуск сервера..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" << 'ENDSSH'
    echo "📋 Выполнение команд на сервере..."
    
    # Создание backup
    if [ -f /opt/aladdin-backend/app/auth/auth.py ]; then
        BACKUP_FILE="/opt/aladdin-backend/app/auth/auth.py.backup_$(date +%Y%m%d_%H%M%S)"
        cp /opt/aladdin-backend/app/auth/auth.py "$BACKUP_FILE"
        echo "✅ Backup создан: $BACKUP_FILE"
    else
        echo "⚠️ Оригинальный файл не найден, backup не создан"
    fi
    
    # Проверка синтаксиса Python
    echo "🔍 Проверка синтаксиса Python..."
    python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py
    if [ $? -eq 0 ]; then
        echo "✅ Синтаксис Python корректен"
    else
        echo "❌ Ошибка синтаксиса Python!"
        exit 1
    fi
    
    # Перезапуск сервера
    echo "🔄 Перезапуск сервера..."
    
    # Попытка через systemd
    if systemctl is-active --quiet aladdin-backend 2>/dev/null; then
        echo "   - Используется systemd"
        systemctl restart aladdin-backend
        sleep 2
        systemctl status aladdin-backend --no-pager -l | head -10
    # Попытка через pm2
    elif command -v pm2 &> /dev/null && pm2 list | grep -q aladdin-backend; then
        echo "   - Используется pm2"
        pm2 restart aladdin-backend
        sleep 2
        pm2 status aladdin-backend
    # Попытка найти процесс uvicorn
    elif pgrep -f "uvicorn.*aladdin" > /dev/null; then
        echo "   - Найден процесс uvicorn, перезапуск..."
        pkill -f "uvicorn.*aladdin"
        sleep 2
        cd /opt/aladdin-backend
        nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/aladdin-backend.log 2>&1 &
        echo "   - Сервер перезапущен через uvicorn"
    else
        echo "⚠️ Не удалось определить способ запуска сервера"
        echo "   Проверьте вручную:"
        echo "   - systemctl status aladdin-backend"
        echo "   - pm2 list"
        echo "   - ps aux | grep uvicorn"
    fi
    
    echo ""
    echo "✅ Команды выполнены на сервере"
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
    echo "=========================================="
    echo ""
    echo "🧪 Тестирование:"
    echo "   curl -H 'Authorization: Bearer YOUR_TOKEN' https://aladdin-ai.ru/api/family/stats"
    echo ""
else
    echo ""
    echo "❌ Ошибка при выполнении команд на сервере!"
    exit 1
fi
