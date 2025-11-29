#!/bin/bash

# ============================================
# АВТОМАТИЧЕСКИЙ BACKUP: Все критичные файлы
# ============================================
# Просто скопируйте на сервер и запустите!
# ============================================

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/referral_backup_${TIMESTAMP}"
BACKUP_ARCHIVE="/tmp/referral_backup_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "🛡️ АВТОМАТИЧЕСКОЕ СОЗДАНИЕ BACKUP'ОВ"
echo "=========================================="
echo "Backup директория: $BACKUP_DIR"
echo ""

# ============================================
# 1. BACKUP БАЗЫ ДАННЫХ
# ============================================

echo "▶ 1. Backup базы данных..."

# Автоматически определяем параметры БД
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-aladdin}"
DB_HOST="${DB_HOST:-localhost}"

# Пробуем найти настройки из переменных окружения или конфигов
if [ -f "/etc/postgresql" ] || [ -f "/var/lib/pgsql" ]; then
    # Пытаемся определить автоматически
    if command -v psql &> /dev/null; then
        # Пробуем подключиться с разными пользователями
        for user in postgres aladdin admin; do
            if psql -h "$DB_HOST" -U "$user" -l &> /dev/null; then
                DB_USER="$user"
                break
            fi
        done
        
        # Пробуем найти базу данных
        if [ -z "$DB_NAME" ]; then
            DB_NAME=$(psql -h "$DB_HOST" -U "$DB_USER" -l -t | grep -v template | head -1 | awk '{print $1}' | xargs)
        fi
    fi
fi

if command -v pg_dump &> /dev/null; then
    echo "   Используем: user=$DB_USER, database=$DB_NAME, host=$DB_HOST"
    
    if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DIR/database_full_backup.sql" 2>/dev/null; then
        echo "   ✅ Backup БД создан: $(du -h "$BACKUP_DIR/database_full_backup.sql" | cut -f1)"
    else
        echo "   ⚠ Не удалось создать backup БД (возможно, нужны другие параметры)"
        echo "   Запустите вручную: pg_dump -h localhost -U user -d database > backup.sql"
    fi
else
    echo "   ⚠ pg_dump не найден, пропускаем"
fi

echo ""

# ============================================
# 2. BACKUP NGINX
# ============================================

echo "▶ 2. Backup Nginx..."

# Ищем все возможные конфигурации
NGINX_CONFIGS=(
    "/etc/nginx/sites-available/aladdin-ai.ru"
    "/etc/nginx/conf.d/aladdin-ai.ru.conf"
    "/etc/nginx/nginx.conf"
)

for config in "${NGINX_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        filename=$(basename "$config")
        sudo cp "$config" "$BACKUP_DIR/nginx_${filename}_${TIMESTAMP}" 2>/dev/null && \
            echo "   ✅ Сохранен: $config" || \
            echo "   ⚠ Не удалось сохранить: $config (нужны права sudo)"
    fi
done

# Сохраняем все конфигурации сайтов
if [ -d "/etc/nginx/sites-available" ]; then
    sudo cp -r /etc/nginx/sites-available "$BACKUP_DIR/nginx_sites_available" 2>/dev/null && \
        echo "   ✅ Сохранены все конфигурации сайтов" || \
        echo "   ⚠ Не удалось сохранить все конфигурации"
fi

echo ""

# ============================================
# 3. BACKUP PYTHON ПРОЕКТА
# ============================================

echo "▶ 3. Backup Python проекта..."

# Ищем проект FastAPI в типичных местах
PROJECT_PATHS=(
    "/var/www/aladdin"
    "/opt/aladdin"
    "/home/*/aladdin"
    "/root/aladdin"
    "$HOME/aladdin"
    "/app"
    "/srv/aladdin"
)

FOUND_PROJECT=""

for path_pattern in "${PROJECT_PATHS[@]}"; do
    for path in $path_pattern; do
        if [ -d "$path" ] && [ -f "$path/main.py" ] || [ -f "$path/app.py" ] || [ -d "$path/app" ]; then
            FOUND_PROJECT="$path"
            break 2
        fi
    done
done

if [ -n "$FOUND_PROJECT" ]; then
    echo "   Найден проект: $FOUND_PROJECT"
    
    # Git backup
    if [ -d "$FOUND_PROJECT/.git" ]; then
        cd "$FOUND_PROJECT"
        git add . 2>/dev/null || true
        git commit -m "Auto backup before referral deployment" 2>/dev/null || true
        git tag "backup-auto-${TIMESTAMP}" 2>/dev/null && \
            echo "   ✅ Git tag создан: backup-auto-${TIMESTAMP}" || \
            echo "   ⚠ Не удалось создать Git tag"
    fi
    
    # Копирование проекта
    cp -r "$FOUND_PROJECT" "$BACKUP_DIR/fastapi_project_backup" 2>/dev/null && \
        echo "   ✅ Проект скопирован" || \
        echo "   ⚠ Не удалось скопировать проект"
    
    # Backup .env файлов
    find "$FOUND_PROJECT" -name ".env*" -type f 2>/dev/null | while read -r env_file; do
        cp "$env_file" "$BACKUP_DIR/" 2>/dev/null && \
            echo "   ✅ Сохранен: $(basename "$env_file")" || true
    done
else
    echo "   ⚠ Проект не найден автоматически"
    echo "   Укажите путь вручную: export PROJECT_PATH=/path/to/project"
fi

echo ""

# ============================================
# 4. BACKUP СТАТИЧЕСКИХ ФАЙЛОВ
# ============================================

echo "▶ 4. Backup статических файлов..."

STATIC_PATHS=(
    "/var/www/aladdin-ai.ru"
    "/var/www/html"
    "/usr/share/nginx/html"
)

for static_path in "${STATIC_PATHS[@]}"; do
    if [ -d "$static_path" ]; then
        sudo cp -r "$static_path" "$BACKUP_DIR/static_$(basename "$static_path")_backup" 2>/dev/null && \
            echo "   ✅ Сохранены: $static_path" || \
            echo "   ⚠ Не удалось сохранить: $static_path"
    fi
done

echo ""

# ============================================
# 5. СОЗДАНИЕ ИНФОРМАЦИОННОГО ФАЙЛА
# ============================================

cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
===========================================
АВТОМАТИЧЕСКИЙ BACKUP
===========================================
Дата: $(date)
Backup директория: $BACKUP_DIR

СОЗДАННЫЕ BACKUP'Ы:
$(ls -lh "$BACKUP_DIR" | tail -n +2)

ВОССТАНОВЛЕНИЕ:
1. База данных:
   psql -h localhost -U user -d database < database_full_backup.sql

2. Nginx:
   sudo cp nginx_* /etc/nginx/sites-available/

3. Проект (Git):
   cd /path/to/project
   git checkout backup-auto-${TIMESTAMP}

===========================================
EOF

echo "   ✅ Информационный файл создан"

echo ""

# ============================================
# 6. СОЗДАНИЕ АРХИВА
# ============================================

echo "▶ 5. Создание архива..."

cd /tmp
tar -czf "$BACKUP_ARCHIVE" "$(basename "$BACKUP_DIR")" 2>/dev/null && \
    echo "   ✅ Архив создан: $BACKUP_ARCHIVE ($(du -h "$BACKUP_ARCHIVE" | cut -f1))" || \
    echo "   ⚠ Не удалось создать архив"

echo ""

# ============================================
# ИТОГ
# ============================================

echo "=========================================="
echo "✅ BACKUP ЗАВЕРШЕН!"
echo ""
echo "Backup директория: $BACKUP_DIR"
if [ -f "$BACKUP_ARCHIVE" ]; then
    echo "Архив: $BACKUP_ARCHIVE"
fi
echo ""
echo "📋 Содержимое backup:"
ls -lh "$BACKUP_DIR"
echo ""
echo "⚠ ВАЖНО: Сохраните backup в безопасное место!"
echo ""


