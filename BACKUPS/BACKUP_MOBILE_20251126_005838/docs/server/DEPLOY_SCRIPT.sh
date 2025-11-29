#!/bin/bash

# ============================================
# СКРИПТ РАЗВЕРТЫВАНИЯ: Реферальная программа
# ============================================
# Сервер: 149.154.65.180
# Сайт: aladdin-ai.ru
# Дата: 21 ноября 2024
# ============================================

set -e  # Остановить при ошибке

echo "🚀 Начало развертывания реферальной программы..."
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================
# ПЕРЕМЕННЫЕ
# ============================================

DB_USER="${DB_USER:-your_user}"
DB_NAME="${DB_NAME:-your_database}"
DB_HOST="${DB_HOST:-localhost}"
FASTAPI_PROJECT_PATH="${FASTAPI_PROJECT_PATH:-/path/to/your/fastapi/project}"
NGINX_SITES_PATH="${NGINX_SITES_PATH:-/etc/nginx/sites-available}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 не установлен"
        exit 1
    fi
}

# ============================================
# ПРОВЕРКА ЗАВИСИМОСТЕЙ
# ============================================

print_step "Проверка зависимостей..."

check_command psql
check_command python3
check_command nginx

print_success "Все зависимости установлены"
echo ""

# ============================================
# ШАГ 1: БАЗА ДАННЫХ
# ============================================

print_step "Шаг 1: Создание таблиц в базе данных..."

if [ -f "$SCRIPT_DIR/REFERRAL_DB_SETUP.sql" ]; then
    read -p "Введите имя пользователя БД [$DB_USER]: " input_user
    DB_USER=${input_user:-$DB_USER}
    
    read -p "Введите имя базы данных [$DB_NAME]: " input_db
    DB_NAME=${input_db:-$DB_NAME}
    
    read -p "Введите хост БД [$DB_HOST]: " input_host
    DB_HOST=${input_host:-$DB_HOST}
    
    print_warning "Выполняется SQL скрипт..."
    if psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$SCRIPT_DIR/REFERRAL_DB_SETUP.sql"; then
        print_success "Таблицы созданы успешно"
    else
        print_error "Ошибка при создании таблиц"
        exit 1
    fi
else
    print_error "Файл REFERRAL_DB_SETUP.sql не найден"
    exit 1
fi

echo ""

# ============================================
# ШАГ 2: API ENDPOINTS
# ============================================

print_step "Шаг 2: Копирование API endpoints..."

if [ -f "$SCRIPT_DIR/REFERRAL_API_ENDPOINTS.py" ]; then
    read -p "Введите путь к проекту FastAPI [$FASTAPI_PROJECT_PATH]: " input_path
    FASTAPI_PROJECT_PATH=${input_path:-$FASTAPI_PROJECT_PATH}
    
    if [ -d "$FASTAPI_PROJECT_PATH" ]; then
        cp "$SCRIPT_DIR/REFERRAL_API_ENDPOINTS.py" "$FASTAPI_PROJECT_PATH/app/routers/"
        print_success "API endpoints скопированы"
        print_warning "Не забудьте настроить импорты и логику!"
    else
        print_warning "Путь к проекту не найден, пропускаем..."
    fi
else
    print_error "Файл REFERRAL_API_ENDPOINTS.py не найден"
fi

echo ""

# ============================================
# ШАГ 3: LANDING СТРАНИЦА
# ============================================

print_step "Шаг 3: Копирование landing страницы..."

if [ -f "$SCRIPT_DIR/REFERRAL_LANDING_PAGE.html" ]; then
    read -p "Введите путь к templates [$FASTAPI_PROJECT_PATH/templates]: " input_templates
    TEMPLATES_PATH=${input_templates:-$FASTAPI_PROJECT_PATH/templates}
    
    if [ -d "$TEMPLATES_PATH" ]; then
        cp "$SCRIPT_DIR/REFERRAL_LANDING_PAGE.html" "$TEMPLATES_PATH/referral_landing.html"
        print_success "Landing страница скопирована"
    else
        print_warning "Путь к templates не найден, пропускаем..."
    fi
else
    print_error "Файл REFERRAL_LANDING_PAGE.html не найден"
fi

echo ""

# ============================================
# ШАГ 4: NGINX
# ============================================

print_step "Шаг 4: Настройка Nginx..."

if [ -f "$SCRIPT_DIR/NGINX_CONFIG.conf" ]; then
    if [ -w "$NGINX_SITES_PATH" ]; then
        read -p "Применить конфигурацию Nginx? (y/n): " apply_nginx
        if [ "$apply_nginx" = "y" ]; then
            sudo cp "$SCRIPT_DIR/NGINX_CONFIG.conf" "$NGINX_SITES_PATH/aladdin-ai.ru"
            print_success "Конфигурация Nginx скопирована"
            
            print_warning "Проверка конфигурации..."
            if sudo nginx -t; then
                print_success "Конфигурация Nginx валидна"
                
                read -p "Перезагрузить Nginx? (y/n): " reload_nginx
                if [ "$reload_nginx" = "y" ]; then
                    sudo systemctl reload nginx
                    print_success "Nginx перезагружен"
                fi
            else
                print_error "Ошибка в конфигурации Nginx"
            fi
        fi
    else
        print_warning "Нет прав для записи в $NGINX_SITES_PATH"
        print_warning "Скопируйте конфигурацию вручную:"
        echo "sudo cp $SCRIPT_DIR/NGINX_CONFIG.conf $NGINX_SITES_PATH/aladdin-ai.ru"
    fi
else
    print_error "Файл NGINX_CONFIG.conf не найден"
fi

echo ""

# ============================================
# ИТОГ
# ============================================

print_success "Развертывание завершено!"
echo ""
print_warning "Следующие шаги:"
echo "1. Настроить импорты в REFERRAL_API_ENDPOINTS.py"
echo "2. Реализовать логику в каждом endpoint"
echo "3. Интегрировать обработчики регистрации и оплаты"
echo "4. Протестировать все компоненты"
echo ""
print_warning "Используйте REFERRAL_TESTING_CHECKLIST.md для тестирования"
echo ""


