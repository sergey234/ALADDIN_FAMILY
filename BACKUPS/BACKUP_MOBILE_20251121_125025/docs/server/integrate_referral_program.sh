#!/bin/bash
# ============================================
# АВТОМАТИЧЕСКАЯ ИНТЕГРАЦИЯ: Реферальная программа
# ============================================
# Сервер: 149.154.65.180
# Дата: 22 ноября 2024
# ============================================

set -e  # Остановить при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Параметры сервера
SERVER="root@149.154.65.180"
SERVER_PASSWORD="Sergio675"
LOCAL_DIR="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

echo -e "${GREEN}=== 🚀 АВТОМАТИЧЕСКАЯ ИНТЕГРАЦИЯ РЕФЕРАЛЬНОЙ ПРОГРАММЫ ===${NC}"
echo ""

# ============================================
# ШАГ 1: База данных
# ============================================

echo -e "${YELLOW}📊 ШАГ 1: Настройка базы данных...${NC}"

# Загрузить SQL скрипт на сервер
echo "Загрузка REFERRAL_DB_SETUP.sql на сервер..."
scp "${LOCAL_DIR}/docs/server/REFERRAL_DB_SETUP.sql" "${SERVER}:/tmp/REFERRAL_DB_SETUP.sql"

# Выполнить SQL скрипт (требует настройки параметров БД)
echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Нужно вручную выполнить SQL скрипт на сервере${NC}"
echo "Команда для выполнения:"
echo "  ssh ${SERVER}"
echo "  psql -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql"
echo ""

# ============================================
# ШАГ 2: Загрузка Python файлов
# ============================================

echo -e "${YELLOW}🐍 ШАГ 2: Загрузка Python файлов...${NC}"

# Определить путь к Python проекту на сервере
PYTHON_PROJECT_PATH="/opt/aladdin-backend"  # Изменить если нужно

echo "Загрузка REFERRAL_API_ENDPOINTS.py..."
scp "${LOCAL_DIR}/docs/server/REFERRAL_API_ENDPOINTS.py" "${SERVER}:${PYTHON_PROJECT_PATH}/app/routers/referral.py"

echo "Загрузка REFERRAL_PAYMENT_INTEGRATION.py..."
scp "${LOCAL_DIR}/docs/server/REFERRAL_PAYMENT_INTEGRATION.py" "${SERVER}:${PYTHON_PROJECT_PATH}/app/referral_payment_integration.py"

echo "Загрузка REFERRAL_SERVER_IMPLEMENTATION.py..."
scp "${LOCAL_DIR}/docs/server/REFERRAL_SERVER_IMPLEMENTATION.py" "${SERVER}:${PYTHON_PROJECT_PATH}/app/referral_implementation.py"

echo -e "${GREEN}✅ Python файлы загружены${NC}"
echo ""

# ============================================
# ШАГ 3: Загрузка landing страницы
# ============================================

echo -e "${YELLOW}🌐 ШАГ 3: Загрузка landing страницы...${NC}"

WEB_ROOT="/var/www/aladdin-ai.ru"  # Изменить если нужно

echo "Загрузка invite.html..."
scp "${LOCAL_DIR}/landing/invite.html" "${SERVER}:${WEB_ROOT}/invite.html"

echo "Настройка прав доступа..."
ssh "${SERVER}" "chmod 644 ${WEB_ROOT}/invite.html"

echo -e "${GREEN}✅ Landing страница загружена${NC}"
echo ""

# ============================================
# ШАГ 4: Настройка Nginx
# ============================================

echo -e "${YELLOW}⚙️  ШАГ 4: Настройка Nginx...${NC}"

# Загрузить конфигурацию
scp "${LOCAL_DIR}/docs/server/NGINX_CONFIG.conf" "${SERVER}:/tmp/nginx_referral.conf"

echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Нужно вручную добавить конфигурацию в Nginx${NC}"
echo "Команды для выполнения:"
echo "  ssh ${SERVER}"
echo "  nano /etc/nginx/sites-available/aladdin-ai.ru"
echo "  # Добавить блок location /invite/ из /tmp/nginx_referral.conf"
echo "  nginx -t"
echo "  systemctl reload nginx"
echo ""

# ============================================
# ШАГ 5: Интеграция в код оплаты
# ============================================

echo -e "${YELLOW}💳 ШАГ 5: Интеграция в код оплаты...${NC}"

echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Нужно вручную интегрировать функции в код оплаты${NC}"
echo "См. инструкции в REFERRAL_INTEGRATION_GUIDE.md"
echo ""

# ============================================
# ИТОГ
# ============================================

echo -e "${GREEN}=== ✅ ИНТЕГРАЦИЯ ЗАВЕРШЕНА ===${NC}"
echo ""
echo "📋 Что сделано автоматически:"
echo "  ✅ Python файлы загружены на сервер"
echo "  ✅ Landing страница загружена"
echo "  ✅ Nginx конфигурация загружена"
echo ""
echo "📋 Что нужно сделать вручную:"
echo "  ⚠️  Выполнить SQL скрипт для создания таблиц"
echo "  ⚠️  Настроить Nginx конфигурацию"
echo "  ⚠️  Интегрировать функции в код оплаты"
echo "  ⚠️  Перезапустить FastAPI приложение"
echo ""
echo "📖 Подробные инструкции: docs/server/REFERRAL_INTEGRATION_GUIDE.md"

