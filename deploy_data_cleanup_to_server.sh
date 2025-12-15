#!/usr/bin/env bash
# -*- coding: utf-8 -*-

"""
Скрипт для деплоя Personal Data Cleanup Agent на сервер

Использование:
    ./deploy_data_cleanup_to_server.sh

Требования:
    - Доступ к серверу через SSH (пароль: Sergio675)
    - Установленный expect (для автоматизации)
"""

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Параметры сервера
SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"
SERVER_PATH="/opt/aladdin-backend"

# Локальные пути
LOCAL_AGENT="security/ai_agents/personal_data_cleanup_agent.py"
LOCAL_ROUTER="security/api/routers/data_cleanup_router.py"
LOCAL_SFM_ENTRY="security/ai_agents/function_registry_entry_data_cleanup.json"
LOCAL_REGISTER_SCRIPT="register_data_cleanup_in_sfm.py"
LOCAL_ADD_TO_MAIN_SCRIPT="add_data_cleanup_to_main.py"

# Удаленные пути
REMOTE_AGENT="${SERVER_PATH}/security/ai_agents/personal_data_cleanup_agent.py"
REMOTE_ROUTER="${SERVER_PATH}/security/api/routers/data_cleanup_router.py"
REMOTE_SFM_ENTRY="${SERVER_PATH}/security/ai_agents/function_registry_entry_data_cleanup.json"
REMOTE_TMP="/tmp"

echo -e "${GREEN}🚀 Начало деплоя Personal Data Cleanup Agent${NC}"
echo ""

# Проверка существования файлов
echo -e "${YELLOW}📋 Проверка файлов...${NC}"
if [ ! -f "$LOCAL_AGENT" ]; then
    echo -e "${RED}❌ Файл не найден: $LOCAL_AGENT${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_ROUTER" ]; then
    echo -e "${RED}❌ Файл не найден: $LOCAL_ROUTER${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_SFM_ENTRY" ]; then
    echo -e "${RED}❌ Файл не найден: $LOCAL_SFM_ENTRY${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_REGISTER_SCRIPT" ]; then
    echo -e "${RED}❌ Файл не найден: $LOCAL_REGISTER_SCRIPT${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_ADD_TO_MAIN_SCRIPT" ]; then
    echo -e "${RED}❌ Файл не найден: $LOCAL_ADD_TO_MAIN_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Все файлы найдены${NC}"
echo ""

# Копирование файлов на сервер
echo -e "${YELLOW}📤 Копирование файлов на сервер...${NC}"

# Копирование агента
echo "Копирование агента..."
expect << EOF
spawn scp "$LOCAL_AGENT" ${SERVER_USER}@${SERVER_IP}:${REMOTE_AGENT}
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

# Копирование роутера
echo "Копирование роутера..."
expect << EOF
spawn scp "$LOCAL_ROUTER" ${SERVER_USER}@${SERVER_IP}:${REMOTE_ROUTER}
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

# Копирование SFM записи
echo "Копирование SFM записи..."
expect << EOF
spawn scp "$LOCAL_SFM_ENTRY" ${SERVER_USER}@${SERVER_IP}:${REMOTE_SFM_ENTRY}
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

# Копирование скриптов регистрации
echo "Копирование скрипта регистрации в SFM..."
expect << EOF
spawn scp "$LOCAL_REGISTER_SCRIPT" ${SERVER_USER}@${SERVER_IP}:${REMOTE_TMP}/
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

echo "Копирование скрипта интеграции в main.py..."
expect << EOF
spawn scp "$LOCAL_ADD_TO_MAIN_SCRIPT" ${SERVER_USER}@${SERVER_IP}:${REMOTE_TMP}/
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

echo -e "${GREEN}✅ Файлы скопированы${NC}"
echo ""

# Проверка синтаксиса на сервере
echo -e "${YELLOW}🔍 Проверка синтаксиса на сервере...${NC}"
expect << EOF
spawn ssh ${SERVER_USER}@${SERVER_IP} "python3 -m py_compile ${REMOTE_AGENT} ${REMOTE_ROUTER} && echo '✅ Синтаксис валиден'"
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

echo ""
echo -e "${GREEN}✅ Деплой завершен!${NC}"
echo ""
echo -e "${YELLOW}📝 Следующие шаги (выполнить на сервере):${NC}"
echo ""
echo "1. Подключиться к серверу:"
echo "   ssh ${SERVER_USER}@${SERVER_IP}"
echo ""
echo "2. Зарегистрировать в SFM:"
echo "   cd ${REMOTE_TMP}"
echo "   python3 register_data_cleanup_in_sfm.py"
echo ""
echo "3. Интегрировать в main.py:"
echo "   python3 add_data_cleanup_to_main.py"
echo ""
echo "4. Перезапустить сервис:"
echo "   systemctl restart aladdin-backend"
echo "   systemctl status aladdin-backend"
echo ""
echo "5. Проверить работу:"
echo "   curl http://localhost:8000/api/data-cleanup/health"
