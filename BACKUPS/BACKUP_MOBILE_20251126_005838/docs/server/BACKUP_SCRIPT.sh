#!/bin/bash

# ============================================
# СКРИПТ СОЗДАНИЯ BACKUP'ОВ
# ============================================
# Используйте ПЕРЕД развертыванием!
# ============================================

set -e

BACKUP_DIR="/tmp/referral_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🛡️ Создание backup'ов перед развертыванием..."
echo "Backup директория: $BACKUP_DIR"
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================
# BACKUP БАЗЫ ДАННЫХ
# ============================================

echo -e "${GREEN}1. Backup базы данных...${NC}"

read -p "Введите имя пользователя БД: " DB_USER
read -p "Введите имя базы данных: " DB_NAME
read -p "Введите хост БД [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

BACKUP_DB_FILE="$BACKUP_DIR/database_backup_$(date +%Y%m%d_%H%M%S).sql"

if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DB_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ Backup базы данных создан: $BACKUP_DB_FILE${NC}"
else
    echo -e "${RED}❌ Ошибка при создании backup базы данных${NC}"
    exit 1
fi

# ============================================
# BACKUP NGINX
# ============================================

echo -e "${GREEN}2. Backup конфигурации Nginx...${NC}"

if [ -f "/etc/nginx/sites-available/aladdin-ai.ru" ]; then
    BACKUP_NGINX_FILE="$BACKUP_DIR/nginx_backup_$(date +%Y%m%d_%H%M%S).conf"
    
    if sudo cp /etc/nginx/sites-available/aladdin-ai.ru "$BACKUP_NGINX_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ Backup Nginx создан: $BACKUP_NGINX_FILE${NC}"
    else
        echo -e "${YELLOW}⚠ Не удалось создать backup Nginx (возможно, нет прав)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Конфигурация Nginx не найдена${NC}"
fi

# ============================================
# BACKUP PYTHON ПРОЕКТА (если используется Git)
# ============================================

echo -e "${GREEN}3. Backup Python проекта...${NC}"

read -p "Введите путь к проекту FastAPI (или нажмите Enter для пропуска): " PROJECT_PATH

if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH" ]; then
    if [ -d "$PROJECT_PATH/.git" ]; then
        cd "$PROJECT_PATH"
        BACKUP_TAG="backup-before-referral-$(date +%Y%m%d)"
        git add .
        git commit -m "Backup before referral program deployment" || true
        git tag "$BACKUP_TAG"
        echo -e "${GREEN}✅ Git backup создан: $BACKUP_TAG${NC}"
    else
        BACKUP_PROJECT_DIR="$BACKUP_DIR/fastapi_project_$(date +%Y%m%d_%H%M%S)"
        cp -r "$PROJECT_PATH" "$BACKUP_PROJECT_DIR"
        echo -e "${GREEN}✅ Backup проекта создан: $BACKUP_PROJECT_DIR${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Пропущено (путь не указан или не найден)${NC}"
fi

# ============================================
# ИТОГ
# ============================================

echo ""
echo -e "${GREEN}✅ Все backup'ы созданы!${NC}"
echo -e "${GREEN}Backup директория: $BACKUP_DIR${NC}"
echo ""
echo -e "${YELLOW}⚠ ВАЖНО: Сохраните путь к backup директории!${NC}"
echo -e "${YELLOW}Для восстановления используйте файлы из: $BACKUP_DIR${NC}"
echo ""


