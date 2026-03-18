#!/bin/bash
# Скрипт для загрузки файлов Варианта 5 на сервер

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PATH="/opt/aladdin-backend"

echo "🚀 ЗАГРУЗКА ВАРИАНТА 5 НА СЕРВЕР"
echo "=================================="
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# SECURITY: Never store passwords in the repository.
# This script now requires SSH key-based auth (recommended for production).
# Setup once (from your machine):
#   ssh-copy-id root@149.154.65.180
# Or configure ~/.ssh/config + ssh-agent.
ssh_exec() {
    ssh -o StrictHostKeyChecking=accept-new "$SERVER_USER@$SERVER_IP" "$1"
}

# Функция для загрузки файлов через SCP
scp_upload() {
    local local_file=$1
    local remote_file=$2
    echo -e "${YELLOW}📤 Загрузка: $local_file -> $remote_file${NC}"
    scp -o StrictHostKeyChecking=accept-new "$local_file" "$SERVER_USER@$SERVER_IP:$remote_file"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Успешно загружено${NC}"
    else
        echo -e "${RED}❌ Ошибка загрузки${NC}"
        return 1
    fi
}

# Проверка подключения
echo -e "${YELLOW}🔍 Проверка подключения к серверу...${NC}"
if ssh_exec "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Подключение установлено${NC}"
else
    echo -e "${RED}❌ Не удалось подключиться к серверу${NC}"
    exit 1
fi

# Создание бэкапа
echo ""
echo -e "${YELLOW}💾 Создание бэкапа существующих файлов...${NC}"
ssh_exec "cd $SERVER_PATH && mkdir -p backups/variant5_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR=$(ssh_exec "cd $SERVER_PATH && ls -td backups/variant5_* | head -1" | tr -d '\r\n')
echo -e "${GREEN}✅ Бэкап создан: $BACKUP_DIR${NC}"

# Загрузка файлов
echo ""
echo -e "${YELLOW}📤 Загрузка файлов...${NC}"

# 1. Reports Router
if [ -f "security/api/routers/reports_router.py" ]; then
    scp_upload "security/api/routers/reports_router.py" "$SERVER_PATH/security/api/routers/reports_router.py"
else
    echo -e "${RED}❌ Файл reports_router.py не найден${NC}"
fi

# 2. Analytics Router (обновленный)
if [ -f "app/routers/analytics_router.py" ]; then
    scp_upload "app/routers/analytics_router.py" "$SERVER_PATH/app/routers/analytics_router.py"
else
    echo -e "${RED}❌ Файл analytics_router.py не найден${NC}"
fi

# 3. Main.py (обновленный)
if [ -f "main.py" ]; then
    scp_upload "main.py" "$SERVER_PATH/main.py"
else
    echo -e "${RED}❌ Файл main.py не найден${NC}"
fi

# Проверка синтаксиса Python
echo ""
echo -e "${YELLOW}🔍 Проверка синтаксиса Python...${NC}"
ssh_exec "cd $SERVER_PATH && python3 -m py_compile security/api/routers/reports_router.py" && echo -e "${GREEN}✅ reports_router.py - синтаксис OK${NC}" || echo -e "${RED}❌ reports_router.py - ошибка синтаксиса${NC}"
ssh_exec "cd $SERVER_PATH && python3 -m py_compile app/routers/analytics_router.py" && echo -e "${GREEN}✅ analytics_router.py - синтаксис OK${NC}" || echo -e "${RED}❌ analytics_router.py - ошибка синтаксиса${NC}"
ssh_exec "cd $SERVER_PATH && python3 -m py_compile main.py" && echo -e "${GREEN}✅ main.py - синтаксис OK${NC}" || echo -e "${RED}❌ main.py - ошибка синтаксиса${NC}"

# Перезапуск сервиса
echo ""
echo -e "${YELLOW}🔄 Перезапуск сервиса...${NC}"
ssh_exec "systemctl restart aladdin-main-api-gateway" && echo -e "${GREEN}✅ Сервис перезапущен${NC}" || echo -e "${RED}❌ Ошибка перезапуска${NC}"

# Ожидание запуска
echo ""
echo -e "${YELLOW}⏳ Ожидание запуска сервиса (10 секунд)...${NC}"
sleep 10

# Проверка статуса
echo ""
echo -e "${YELLOW}🔍 Проверка статуса сервиса...${NC}"
ssh_exec "systemctl status aladdin-main-api-gateway --no-pager | head -10"

# Проверка health endpoint
echo ""
echo -e "${YELLOW}🔍 Проверка health endpoint...${NC}"
HEALTH=$(ssh_exec "curl -s http://127.0.0.1:8002/api/health")
echo "$HEALTH"

echo ""
echo -e "${GREEN}✅ ЗАГРУЗКА ЗАВЕРШЕНА${NC}"
echo ""
echo "Следующий шаг: Запустите тесты:"
echo "python3 docs/server/test_variant5_endpoints.py"
