#!/bin/bash
# ============================================================================
# ДЕПЛОЙ: Исправление JWT 401 - 4 файла
# ============================================================================
# Дата: 2026-03-17
# Цель: Задеплоить исправления JWT_SECRET на сервер
# ============================================================================

set -e  # Остановить при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-149.154.65.180}"
SERVER_PATH="${SERVER_PATH:-/opt/aladdin-backend}"
LOCAL_PATH="$(cd "$(dirname "$0")/../.." && pwd)"

# Файлы для деплоя
FILES=(
    "app/auth/auth.py"
    "backend/app/services/jwt_service.py"
    "app/auth/__init__.py"
    "app/routers/analytics_router.py"
)

echo "============================================================================"
echo "🚀 ДЕПЛОЙ: Исправление JWT 401 - 4 файла"
echo "============================================================================"
echo "📅 Дата: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🌐 Сервер: ${SERVER_USER}@${SERVER_HOST}"
echo "📁 Путь на сервере: ${SERVER_PATH}"
echo "📁 Локальный путь: ${LOCAL_PATH}"
echo "============================================================================"
echo

# Проверка существования файлов локально
echo "🔍 Проверка локальных файлов..."
for file in "${FILES[@]}"; do
    local_file="${LOCAL_PATH}/${file}"
    if [ -f "$local_file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - НЕ НАЙДЕН!"
        exit 1
    fi
done
echo

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_HOST}" "echo 'Connected'" 2>/dev/null; then
    echo "   ✅ Подключение к серверу успешно"
else
    echo "   ❌ Не удалось подключиться к серверу"
    echo "   💡 Проверьте:"
    echo "      - SSH ключи настроены"
    echo "      - Сервер доступен: ${SERVER_HOST}"
    echo "      - Пользователь: ${SERVER_USER}"
    exit 1
fi
echo

# Создание backup на сервере
echo "📦 Создание backup на сервере..."
BACKUP_DIR="${SERVER_PATH}/backup_jwt_fix_$(date +%Y%m%d_%H%M%S)"
ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${BACKUP_DIR}"

for file in "${FILES[@]}"; do
    server_file="${SERVER_PATH}/${file}"
    backup_file="${BACKUP_DIR}/$(basename ${file}).backup"
    
    if ssh "${SERVER_USER}@${SERVER_HOST}" "[ -f ${server_file} ]"; then
        ssh "${SERVER_USER}@${SERVER_HOST}" "cp ${server_file} ${backup_file}"
        echo "   ✅ Backup создан: ${file} → ${backup_file}"
    else
        echo "   ⚠️  Файл не существует на сервере: ${file} (будет создан)"
    fi
done
echo "   ✅ Backup создан в: ${BACKUP_DIR}"
echo

# Деплой файлов
echo "📤 Деплой файлов на сервер..."
for file in "${FILES[@]}"; do
    local_file="${LOCAL_PATH}/${file}"
    server_file="${SERVER_PATH}/${file}"
    server_dir="$(dirname ${server_file})"
    
    echo "   📄 Деploy: ${file}"
    
    # Создать директорию на сервере если нужно
    ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${server_dir}"
    
    # Скопировать файл
    scp "${local_file}" "${SERVER_USER}@${SERVER_HOST}:${server_file}"
    
    if [ $? -eq 0 ]; then
        echo "      ✅ Успешно задеплоен"
    else
        echo "      ❌ Ошибка деплоя!"
        exit 1
    fi
done
echo

# Проверка деплоя
echo "✅ Проверка деплоя..."
for file in "${FILES[@]}"; do
    server_file="${SERVER_PATH}/${file}"
    
    case "$file" in
        "app/auth/auth.py")
            if ssh "${SERVER_USER}@${SERVER_HOST}" "grep -q 'aladdin-super-secret-key-change-in-production' ${server_file} && grep -q 'leeway=60' ${server_file}"; then
                echo "   ✅ ${file} - исправления найдены"
            else
                echo "   ❌ ${file} - исправления НЕ найдены!"
            fi
            ;;
        "backend/app/services/jwt_service.py")
            if ssh "${SERVER_USER}@${SERVER_HOST}" "grep -q 'aladdin-super-secret-key-change-in-production' ${server_file} && grep -q 'leeway=60' ${server_file} && grep -q 'import os' ${server_file}"; then
                echo "   ✅ ${file} - исправления найдены"
            else
                echo "   ❌ ${file} - исправления НЕ найдены!"
            fi
            ;;
        "app/auth/__init__.py")
            if ssh "${SERVER_USER}@${SERVER_HOST}" "grep -q 'aladdin-super-secret-key-change-in-production' ${server_file}"; then
                echo "   ✅ ${file} - исправления найдены"
            else
                echo "   ❌ ${file} - исправления НЕ найдены!"
            fi
            ;;
        "app/routers/analytics_router.py")
            if ssh "${SERVER_USER}@${SERVER_HOST}" "grep -q 'from app.auth.auth import get_current_user' ${server_file} && ! grep -A 5 'except ImportError:' ${server_file} | grep -q 'get_current_user'"; then
                echo "   ✅ ${file} - исправления найдены"
            else
                echo "   ❌ ${file} - исправления НЕ найдены!"
            fi
            ;;
    esac
done
echo

# Перезапуск сервера
echo "🔄 Перезапуск сервера..."
echo "   💡 Выберите метод перезапуска:"
echo "      1) systemd (sudo systemctl restart aladdin-api)"
echo "      2) pm2 (pm2 restart aladdin-api)"
echo "      3) supervisor (supervisorctl restart aladdin-api)"
echo "      4) Пропустить перезапуск"
read -p "   Выбор (1-4): " restart_choice

case "$restart_choice" in
    1)
        ssh "${SERVER_USER}@${SERVER_HOST}" "sudo systemctl restart aladdin-api && sudo systemctl status aladdin-api --no-pager"
        echo "   ✅ Сервер перезапущен через systemd"
        ;;
    2)
        ssh "${SERVER_USER}@${SERVER_HOST}" "pm2 restart aladdin-api && pm2 status aladdin-api"
        echo "   ✅ Сервер перезапущен через pm2"
        ;;
    3)
        ssh "${SERVER_USER}@${SERVER_HOST}" "supervisorctl restart aladdin-api && supervisorctl status aladdin-api"
        echo "   ✅ Сервер перезапущен через supervisor"
        ;;
    4)
        echo "   ⚠️  Перезапуск пропущен (нужно перезапустить вручную!)"
        ;;
    *)
        echo "   ⚠️  Неверный выбор, перезапуск пропущен"
        ;;
esac
echo

echo "============================================================================"
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "============================================================================"
echo "📦 Backup: ${BACKUP_DIR}"
echo "📤 Задеплоено файлов: ${#FILES[@]}"
echo "🔄 Сервер: перезапущен (если выбран)"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Запустить тест: python3 docs/server/test_protected_endpoints_jwt_fix.py"
echo "   2. Проверить логи сервера"
echo "   3. Убедиться, что 401 ошибок нет"
echo "============================================================================"
