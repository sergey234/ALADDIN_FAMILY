#!/usr/bin/env bash
# -*- coding: utf-8 -*-

"""
Полный скрипт деплоя Personal Data Cleanup Agent
Включает: регистрацию в SFM, интеграцию в main.py, перезапуск сервиса

Использование:
    ./complete_data_cleanup_deployment.sh
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

echo -e "${GREEN}🚀 Полный деплой Personal Data Cleanup Agent${NC}"
echo ""

# Шаг 1: Регистрация в SFM
echo -e "${YELLOW}📝 Шаг 1: Регистрация в SFM...${NC}"
expect << EOF
spawn ssh ${SERVER_USER}@${SERVER_IP} "cd /tmp && python3 register_data_cleanup_in_sfm.py"
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
echo -e "${GREEN}✅ Регистрация в SFM завершена${NC}"
echo ""

# Шаг 2: Интеграция в main.py
echo -e "${YELLOW}📝 Шаг 2: Интеграция в main.py...${NC}"
expect << EOF
spawn ssh ${SERVER_USER}@${SERVER_IP} "cd /tmp && python3 add_data_cleanup_to_main.py"
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
echo -e "${GREEN}✅ Интеграция в main.py завершена${NC}"
echo ""

# Шаг 3: Перезапуск сервиса
echo -e "${YELLOW}📝 Шаг 3: Перезапуск сервиса...${NC}"
expect << EOF
spawn ssh ${SERVER_USER}@${SERVER_IP} "systemctl restart aladdin-backend && systemctl status aladdin-backend --no-pager -l | head -20"
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
echo -e "${GREEN}✅ Сервис перезапущен${NC}"
echo ""

# Шаг 4: Проверка работы
echo -e "${YELLOW}📝 Шаг 4: Проверка работы...${NC}"
expect << EOF
spawn ssh ${SERVER_USER}@${SERVER_IP} "sleep 3 && curl -s http://localhost:8000/api/data-cleanup/health | python3 -m json.tool || echo 'Ошибка проверки'"
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
echo -e "${GREEN}✅ Деплой полностью завершен!${NC}"
echo ""
echo -e "${YELLOW}📋 Проверка всех endpoints:${NC}"
echo "curl http://localhost:8000/api/data-cleanup/health"
echo "curl http://localhost:8000/api/data-cleanup/scan-status?user_id=test123"
echo ""
