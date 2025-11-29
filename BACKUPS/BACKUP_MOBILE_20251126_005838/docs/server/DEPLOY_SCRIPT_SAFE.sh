#!/bin/bash

# ============================================
# БЕЗОПАСНЫЙ СКРИПТ РАЗВЕРТЫВАНИЯ
# ============================================
# Версия: 2.0 (с защитами)
# Сервер: 149.154.65.180
# Дата: 21 ноября 2024
# ============================================

set -e  # Остановить при ошибке

echo "🛡️ БЕЗОПАСНЫЙ скрипт развертывания реферальной программы"
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================
# ПЕРЕМЕННЫЕ
# ============================================

DRY_RUN=false
AUTO_BACKUP=true
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/tmp/referral_backup_$(date +%Y%m%d_%H%M%S)}"

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

confirm() {
    read -p "$(echo -e ${YELLOW}$1 (y/n): ${NC})" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# ============================================
# ПРОВЕРКА РЕЖИМА DRY-RUN
# ============================================

if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    print_warning "РЕЖИМ DRY-RUN: Команды будут показаны, но не выполнены"
    echo ""
fi

# ============================================
# СОЗДАНИЕ BACKUP'ОВ
# ============================================

create_backups() {
    print_step "Создание backup'ов..."
    
    mkdir -p "$BACKUP_DIR"
    print_info "Backup директория: $BACKUP_DIR"
    
    # Backup базы данных
    if command -v pg_dump &> /dev/null; then
        read -p "Введите имя пользователя БД: " DB_USER
        read -p "Введите имя базы данных: " DB_NAME
        read -p "Введите хост БД [localhost]: " DB_HOST
        DB_HOST=${DB_HOST:-localhost}
        
        BACKUP_DB_FILE="$BACKUP_DIR/database_backup_$(date +%Y%m%d_%H%M%S).sql"
        
        if [ "$DRY_RUN" = true ]; then
            print_info "DRY-RUN: pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DB_FILE"
        else
            if confirm "Создать backup базы данных?"; then
                print_info "Создание backup базы данных..."
                if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DB_FILE" 2>/dev/null; then
                    print_success "Backup базы данных создан: $BACKUP_DB_FILE"
                else
                    print_error "Не удалось создать backup базы данных"
                    if ! confirm "Продолжить без backup базы данных?"; then
                        exit 1
                    fi
                fi
            fi
        fi
    else
        print_warning "pg_dump не найден, пропускаем backup БД"
    fi
    
    # Backup Nginx конфигурации
    if [ -f "/etc/nginx/sites-available/aladdin-ai.ru" ]; then
        BACKUP_NGINX_FILE="$BACKUP_DIR/nginx_backup_$(date +%Y%m%d_%H%M%S).conf"
        
        if [ "$DRY_RUN" = true ]; then
            print_info "DRY-RUN: sudo cp /etc/nginx/sites-available/aladdin-ai.ru $BACKUP_NGINX_FILE"
        else
            if confirm "Создать backup конфигурации Nginx?"; then
                print_info "Создание backup Nginx..."
                if sudo cp /etc/nginx/sites-available/aladdin-ai.ru "$BACKUP_NGINX_FILE" 2>/dev/null; then
                    print_success "Backup Nginx создан: $BACKUP_NGINX_FILE"
                else
                    print_error "Не удалось создать backup Nginx"
                    if ! confirm "Продолжить без backup Nginx?"; then
                        exit 1
                    fi
                fi
            fi
        fi
    else
        print_info "Конфигурация Nginx не найдена (возможно, еще не настроена)"
    fi
    
    print_success "Backup'ы созданы в: $BACKUP_DIR"
    echo ""
}

# ============================================
# ПРОВЕРКА ФАЙЛОВ
# ============================================

check_files() {
    print_step "Проверка файлов..."
    
    REQUIRED_FILES=(
        "REFERRAL_DB_SETUP.sql"
        "REFERRAL_API_ENDPOINTS.py"
        "REFERRAL_LANDING_PAGE.html"
        "NGINX_CONFIG.conf"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$SCRIPT_DIR/$file" ]; then
            print_success "$file найден"
        else
            print_error "$file не найден!"
            exit 1
        fi
    done
    
    echo ""
}

# ============================================
# БАЗА ДАННЫХ
# ============================================

setup_database() {
    print_step "Настройка базы данных..."
    
    if [ ! -f "$SCRIPT_DIR/REFERRAL_DB_SETUP.sql" ]; then
        print_error "Файл REFERRAL_DB_SETUP.sql не найден"
        return 1
    fi
    
    if [ "$DRY_RUN" = true ]; then
        print_info "DRY-RUN: psql -h localhost -U user -d database -f REFERRAL_DB_SETUP.sql"
        return 0
    fi
    
    if ! confirm "Выполнить SQL скрипт для создания таблиц?"; then
        print_warning "Пропущено создание таблиц"
        return 0
    fi
    
    read -p "Введите имя пользователя БД: " DB_USER
    read -p "Введите имя базы данных: " DB_NAME
    read -p "Введите хост БД [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    print_warning "ВНИМАНИЕ: Это создаст таблицы в базе данных!"
    if ! confirm "Продолжить?"; then
        print_warning "Отменено"
        return 0
    fi
    
    if psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$SCRIPT_DIR/REFERRAL_DB_SETUP.sql" 2>&1; then
        print_success "Таблицы созданы успешно"
    else
        print_error "Ошибка при создании таблиц"
        if confirm "Продолжить несмотря на ошибку?"; then
            return 0
        else
            exit 1
        fi
    fi
    
    echo ""
}

# ============================================
# NGINX
# ============================================

setup_nginx() {
    print_step "Настройка Nginx..."
    
    if [ ! -f "$SCRIPT_DIR/NGINX_CONFIG.conf" ]; then
        print_error "Файл NGINX_CONFIG.conf не найден"
        return 1
    fi
    
    if [ "$DRY_RUN" = true ]; then
        print_info "DRY-RUN: sudo cp NGINX_CONFIG.conf /etc/nginx/sites-available/aladdin-ai.ru"
        print_info "DRY-RUN: sudo nginx -t"
        print_info "DRY-RUN: sudo systemctl reload nginx"
        return 0
    fi
    
    if ! confirm "Применить конфигурацию Nginx?"; then
        print_warning "Пропущена настройка Nginx"
        return 0
    fi
    
    print_warning "ВНИМАНИЕ: Это перезапишет существующую конфигурацию!"
    if ! confirm "Продолжить?"; then
        print_warning "Отменено"
        return 0
    fi
    
    # Проверка существующей конфигурации
    if [ -f "/etc/nginx/sites-available/aladdin-ai.ru" ]; then
        print_warning "Существующая конфигурация будет перезаписана!"
        if ! confirm "Продолжить?"; then
            print_warning "Отменено"
            return 0
        fi
    fi
    
    if sudo cp "$SCRIPT_DIR/NGINX_CONFIG.conf" /etc/nginx/sites-available/aladdin-ai.ru; then
        print_success "Конфигурация скопирована"
    else
        print_error "Ошибка при копировании конфигурации"
        return 1
    fi
    
    print_info "Проверка конфигурации..."
    if sudo nginx -t; then
        print_success "Конфигурация валидна"
        
        if confirm "Перезагрузить Nginx?"; then
            if sudo systemctl reload nginx; then
                print_success "Nginx перезагружен"
            else
                print_error "Ошибка при перезагрузке Nginx"
                return 1
            fi
        fi
    else
        print_error "Ошибка в конфигурации Nginx!"
        print_warning "Конфигурация НЕ применена"
        return 1
    fi
    
    echo ""
}

# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

main() {
    echo "=========================================="
    echo "  БЕЗОПАСНОЕ РАЗВЕРТЫВАНИЕ"
    echo "=========================================="
    echo ""
    
    # Проверка файлов
    check_files
    
    # Создание backup'ов
    if [ "$AUTO_BACKUP" = true ]; then
        if confirm "Создать backup'ы перед развертыванием?"; then
            create_backups
        fi
    fi
    
    # Подтверждение
    print_warning "ВНИМАНИЕ: Этот скрипт изменит вашу систему!"
    print_info "Убедитесь, что вы создали backup'ы"
    echo ""
    
    if ! confirm "Продолжить развертывание?"; then
        print_warning "Отменено пользователем"
        exit 0
    fi
    
    echo ""
    
    # База данных
    setup_database
    
    # Nginx
    setup_nginx
    
    # Итог
    echo ""
    print_success "Развертывание завершено!"
    echo ""
    print_info "Следующие шаги:"
    echo "1. Интегрировать Python код в ваш проект"
    echo "2. Разместить HTML файл"
    echo "3. Протестировать все компоненты"
    echo ""
    print_info "Backup'ы сохранены в: $BACKUP_DIR"
    echo ""
}

# Запуск
main


