#!/bin/bash
# -*- coding: utf-8 -*-
#
# 😴 ПЕРЕВОД ANTI-TRACKER AGENT В СПЯЩИЙ РЕЖИМ НА СЕРВЕРЕ
#

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация сервера
SERVER="${ALADDIN_SERVER:-149.154.65.180}"
SERVER_USER="root"
SERVER_PASS="${ALADDIN_SERVER_PASS:-Sergio675}"

REMOTE_BACKEND="/opt/aladdin-backend"
REMOTE_TMP="/tmp"
LOCAL_SCRIPT="put_anti_tracker_to_sleep.py"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}😴 ПЕРЕВОД ANTI-TRACKER AGENT В СПЯЩИЙ РЕЖИМ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Проверка файла локально
if [ ! -f "$LOCAL_SCRIPT" ]; then
    echo -e "${RED}❌ Скрипт не найден: $LOCAL_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Скрипт найден${NC}"
echo ""

# Копирование скрипта на сервер
echo -e "${YELLOW}📤 Копирование скрипта на сервер...${NC}"

expect << EOF
set timeout 30
spawn scp "$LOCAL_SCRIPT" ${SERVER_USER}@${SERVER}:${REMOTE_TMP}/
expect {
    "password:" {
        send "${SERVER_PASS}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

echo -e "${GREEN}✅ Скрипт скопирован${NC}"
echo ""

# Выполнение скрипта на сервере
echo -e "${YELLOW}😴 Перевод агента в спящий режим...${NC}"

expect << EOF
set timeout 60
spawn ssh ${SERVER_USER}@${SERVER} "cd ${REMOTE_TMP} && python3 put_anti_tracker_to_sleep.py"
expect {
    "password:" {
        send "${SERVER_PASS}\r"
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
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ АГЕНТ ПЕРЕВЕДЕН В СПЯЩИЙ РЕЖИМ!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Проверка статуса:${NC}"
echo "   ssh ${SERVER_USER}@${SERVER} 'cat /opt/aladdin-backend/data/sfm/function_registry.json | python3 -c \"import sys, json; r=json.load(sys.stdin); print(\\\"Status:\\\", r.get(\\\"anti_tracker_agent\\\", {}).get(\\\"status\\\", \\\"unknown\\\"))\"'"
echo ""
