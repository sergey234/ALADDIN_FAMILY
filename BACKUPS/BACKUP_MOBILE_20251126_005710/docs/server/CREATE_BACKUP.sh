#!/bin/bash

# ============================================
# ПОЛНЫЙ BACKUP: Все критичные файлы
# ============================================
# Версия: 2.0
# Дата: 21 ноября 2024
# ============================================

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================
# НАСТРОЙКИ
# ============================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/referral_backup_${TIMESTAMP}"
BACKUP_ARCHIVE="/tmp/referral_backup_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/nginx"
mkdir -p "$BACKUP_DIR/project"
mkdir -p "$BACKUP_DIR/env"
mkdir -p "$BACKUP_DIR/logs"

echo -e "${BLUE}🛡️  СОЗДАНИЕ ПОЛНОГО BACKUP'А${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}Backup директория: $BACKUP_DIR${NC}"
echo -e "${GREEN}Архив будет создан: $BACKUP_ARCHIVE${NC}"
echo ""

# ============================================
# ФУНКЦИИ
# ============================================

print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================
# 1. BACKUP БАЗЫ ДАННЫХ
# ============================================

print_step "1. Backup базы данных..."

if command -v pg_dump &> /dev/null; then
    read -p "Введите имя пользователя БД: " DB_USER
    read -p "Введите имя базы данных: " DB_NAME
    read -p "Введите хост БД [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    BACKUP_DB_FILE="$BACKUP_DIR/database/full_backup_${TIMESTAMP}.sql"
    BACKUP_DB_SCHEMA="$BACKUP_DIR/database/schema_only_${TIMESTAMP}.sql"
    
    print_info "Создание полного backup базы данных..."
    if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DB_FILE" 2>/dev/null; then
        print_success "Полный backup БД создан: $BACKUP_DB_FILE"
        
        # Также создаем backup только структуры
        print_info "Создание backup структуры БД..."
        if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" --schema-only > "$BACKUP_DB_SCHEMA" 2>/dev/null; then
            print_success "Backup структуры БД создан: $BACKUP_DB_SCHEMA"
        fi
    else
        print_error "Ошибка при создании backup БД"
        print_warning "Продолжаем без backup БД..."
    fi
else
    print_warning "pg_dump не найден, пропускаем backup БД"
fi

echo ""

# ============================================
# 2. BACKUP NGINX
# ============================================

print_step "2. Backup конфигурации Nginx..."

# Главная конфигурация
if [ -f "/etc/nginx/nginx.conf" ]; then
    if sudo cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx/nginx.conf.backup_${TIMESTAMP}" 2>/dev/null; then
        print_success "Backup главной конфигурации Nginx создан"
    else
        print_warning "Не удалось создать backup главной конфигурации (возможно, нет прав)"
    fi
fi

# Конфигурация сайта
if [ -f "/etc/nginx/sites-available/aladdin-ai.ru" ]; then
    if sudo cp /etc/nginx/sites-available/aladdin-ai.ru "$BACKUP_DIR/nginx/aladdin-ai.ru.backup_${TIMESTAMP}" 2>/dev/null; then
        print_success "Backup конфигурации сайта создан"
    else
        print_warning "Не удалось создать backup конфигурации сайта"
    fi
fi

# Все конфигурации сайтов
if [ -d "/etc/nginx/sites-available" ]; then
    if sudo cp -r /etc/nginx/sites-available/* "$BACKUP_DIR/nginx/sites-available/" 2>/dev/null; then
        print_success "Backup всех конфигураций сайтов создан"
    else
        print_warning "Не удалось создать backup всех конфигураций"
    fi
fi

# SSL сертификаты (только информация о путях)
if [ -d "/etc/letsencrypt/live/aladdin-ai.ru" ]; then
    sudo ls -la /etc/letsencrypt/live/aladdin-ai.ru/ > "$BACKUP_DIR/nginx/ssl_certificates_info.txt" 2>/dev/null || true
    print_info "Информация о SSL сертификатах сохранена"
fi

echo ""

# ============================================
# 3. BACKUP PYTHON ПРОЕКТА
# ============================================

print_step "3. Backup Python/FastAPI проекта..."

read -p "Введите путь к проекту FastAPI (или нажмите Enter для пропуска): " PROJECT_PATH

if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH" ]; then
    PROJECT_BACKUP_DIR="$BACKUP_DIR/project/fastapi_project_${TIMESTAMP}"
    
    # Проверка Git
    if [ -d "$PROJECT_PATH/.git" ]; then
        print_info "Обнаружен Git репозиторий"
        cd "$PROJECT_PATH"
        
        # Создать Git tag
        BACKUP_TAG="backup-before-referral-${TIMESTAMP}"
        if git tag "$BACKUP_TAG" 2>/dev/null; then
            print_success "Git tag создан: $BACKUP_TAG"
        fi
        
        # Сохранить Git статус
        git status > "$BACKUP_DIR/project/git_status.txt" 2>/dev/null || true
        git log -1 > "$BACKUP_DIR/project/git_last_commit.txt" 2>/dev/null || true
    fi
    
    # Копирование проекта
    print_info "Копирование проекта..."
    if cp -r "$PROJECT_PATH" "$PROJECT_BACKUP_DIR" 2>/dev/null; then
        print_success "Backup проекта создан: $PROJECT_BACKUP_DIR"
        
        # Удалить большие файлы из backup (если есть)
        find "$PROJECT_BACKUP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "$PROJECT_BACKUP_DIR" -type d -name ".git" -exec rm -rf {} + 2>/dev/null || true
        find "$PROJECT_BACKUP_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
        
        print_info "Очистка временных файлов выполнена"
    else
        print_error "Ошибка при копировании проекта"
    fi
else
    print_warning "Путь к проекту не указан или не найден, пропускаем"
fi

echo ""

# ============================================
# 4. BACKUP ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ============================================

print_step "4. Backup переменных окружения..."

if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH" ]; then
    # Ищем .env файлы
    find "$PROJECT_PATH" -name ".env" -o -name ".env.*" 2>/dev/null | while read -r env_file; do
        if [ -f "$env_file" ]; then
            RELATIVE_PATH=$(echo "$env_file" | sed "s|$PROJECT_PATH/||")
            BACKUP_ENV_FILE="$BACKUP_DIR/env/${RELATIVE_PATH//\//_}_${TIMESTAMP}"
            cp "$env_file" "$BACKUP_ENV_FILE" 2>/dev/null && print_success "Backup .env файла: $RELATIVE_PATH" || true
        fi
    done
fi

# Также проверяем системные переменные окружения
printenv > "$BACKUP_DIR/env/system_env_${TIMESTAMP}.txt" 2>/dev/null || true
print_info "Системные переменные окружения сохранены"

echo ""

# ============================================
# 5. BACKUP СТАТИЧЕСКИХ ФАЙЛОВ
# ============================================

print_step "5. Backup статических файлов..."

if [ -d "/var/www/aladdin-ai.ru" ]; then
    if sudo cp -r /var/www/aladdin-ai.ru "$BACKUP_DIR/static_files_${TIMESTAMP}" 2>/dev/null; then
        print_success "Backup статических файлов создан"
    else
        print_warning "Не удалось создать backup статических файлов"
    fi
else
    print_info "Директория статических файлов не найдена"
fi

echo ""

# ============================================
# 6. BACKUP ЛОГОВ
# ============================================

print_step "6. Backup логов..."

# Логи Nginx
if [ -f "/var/log/nginx/error.log" ]; then
    sudo tail -n 1000 /var/log/nginx/error.log > "$BACKUP_DIR/logs/nginx_error.log" 2>/dev/null || true
    print_info "Последние 1000 строк error.log сохранены"
fi

if [ -f "/var/log/nginx/access.log" ]; then
    sudo tail -n 1000 /var/log/nginx/access.log > "$BACKUP_DIR/logs/nginx_access.log" 2>/dev/null || true
    print_info "Последние 1000 строк access.log сохранены"
fi

# Логи приложения (если есть)
if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH/logs" ]; then
    cp -r "$PROJECT_PATH/logs" "$BACKUP_DIR/logs/app_logs" 2>/dev/null || true
    print_info "Логи приложения сохранены"
fi

echo ""

# ============================================
# 7. СОЗДАНИЕ ИНФОРМАЦИОННОГО ФАЙЛА
# ============================================

print_step "7. Создание информационного файла..."

INFO_FILE="$BACKUP_DIR/BACKUP_INFO.txt"
cat > "$INFO_FILE" << EOF
===========================================
BACKUP ИНФОРМАЦИЯ
===========================================
Дата создания: $(date)
Версия скрипта: 2.0
Backup директория: $BACKUP_DIR

СОЗДАННЫЕ BACKUP'Ы:
- База данных: database/
- Nginx: nginx/
- Python проект: project/
- Переменные окружения: env/
- Логи: logs/

ВОССТАНОВЛЕНИЕ:
1. База данных:
   psql -h localhost -U user -d database < database/full_backup_${TIMESTAMP}.sql

2. Nginx:
   sudo cp nginx/aladdin-ai.ru.backup_${TIMESTAMP} /etc/nginx/sites-available/aladdin-ai.ru
   sudo nginx -t && sudo systemctl reload nginx

3. Python проект:
   cp -r project/fastapi_project_${TIMESTAMP}/* /path/to/project/

ВАЖНО: Сохраните этот backup в безопасном месте!
===========================================
EOF

print_success "Информационный файл создан: $INFO_FILE"

echo ""

# ============================================
# 8. СОЗДАНИЕ АРХИВА
# ============================================

print_step "8. Создание архива..."

if command -v tar &> /dev/null; then
    print_info "Создание tar.gz архива..."
    cd "$(dirname "$BACKUP_DIR")"
    if tar -czf "$BACKUP_ARCHIVE" "$(basename "$BACKUP_DIR")" 2>/dev/null; then
        print_success "Архив создан: $BACKUP_ARCHIVE"
        
        # Показать размер
        ARCHIVE_SIZE=$(du -h "$BACKUP_ARCHIVE" | cut -f1)
        print_info "Размер архива: $ARCHIVE_SIZE"
    else
        print_warning "Не удалось создать архив"
    fi
else
    print_warning "tar не найден, архив не создан"
fi

echo ""

# ============================================
# ИТОГ
# ============================================

echo -e "${BLUE}==========================================${NC}"
print_success "BACKUP ЗАВЕРШЕН!"
echo ""
print_info "Backup директория: $BACKUP_DIR"
if [ -f "$BACKUP_ARCHIVE" ]; then
    print_info "Архив: $BACKUP_ARCHIVE"
fi
echo ""
print_warning "⚠ ВАЖНО:"
echo "1. Сохраните backup в безопасное место"
echo "2. Проверьте, что все файлы сохранены"
echo "3. Не удаляйте backup до завершения развертывания"
echo ""
print_info "Информация о backup: $INFO_FILE"
echo ""


