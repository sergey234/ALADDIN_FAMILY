#!/bin/bash
# -*- coding: utf-8 -*-
#
# 🚗 ДЕПЛОЙ CRASH DETECTION AGENT НА СЕРВЕР
#
# Автоматический деплой Crash Detection Agent на сервер
# Дата: 12 декабря 2025
#

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация сервера
SERVER="${ALADDIN_SERVER:-149.154.65.180}"
SERVER_USER="root"  # Всегда используем root
SERVER_PASS="${ALADDIN_SERVER_PASS:-Sergio675}"

# Пути
LOCAL_AGENT="security/ai_agents/crash_detection_agent.py"
LOCAL_ROUTER="security/api/routers/crash_detection_router.py"
LOCAL_REGISTRY="security/ai_agents/function_registry_entry_crash_detection.json"
LOCAL_REGISTER_SCRIPT="register_crash_detection_in_sfm.py"
LOCAL_MAIN_SCRIPT="add_crash_detection_to_main.py"

REMOTE_BACKEND="/opt/aladdin-backend"
REMOTE_AGENT_DIR="${REMOTE_BACKEND}/security/ai_agents"
REMOTE_ROUTER_DIR="${REMOTE_BACKEND}/security/api/routers"
REMOTE_TMP="/tmp"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚗 ДЕПЛОЙ CRASH DETECTION AGENT НА СЕРВЕР${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Проверка файлов локально
echo -e "${YELLOW}📋 Проверка файлов локально...${NC}"

if [ ! -f "$LOCAL_AGENT" ]; then
    echo -e "${RED}❌ Файл агента не найден: $LOCAL_AGENT${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_ROUTER" ]; then
    echo -e "${RED}❌ Файл router не найден: $LOCAL_ROUTER${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_REGISTRY" ]; then
    echo -e "${RED}❌ Файл registry не найден: $LOCAL_REGISTRY${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_REGISTER_SCRIPT" ]; then
    echo -e "${RED}❌ Скрипт регистрации не найден: $LOCAL_REGISTER_SCRIPT${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_MAIN_SCRIPT" ]; then
    echo -e "${RED}❌ Скрипт интеграции не найден: $LOCAL_MAIN_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Все файлы найдены${NC}"
echo ""

# Проверка синтаксиса
echo -e "${YELLOW}🔍 Проверка синтаксиса Python...${NC}"

if ! python3 -m py_compile "$LOCAL_AGENT" 2>/dev/null; then
    echo -e "${RED}❌ Ошибка синтаксиса в $LOCAL_AGENT${NC}"
    exit 1
fi

if ! python3 -m py_compile "$LOCAL_ROUTER" 2>/dev/null; then
    echo -e "${RED}❌ Ошибка синтаксиса в $LOCAL_ROUTER${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Синтаксис корректен${NC}"
echo ""

# Копирование файлов на сервер
echo -e "${YELLOW}📤 Копирование файлов на сервер...${NC}"

# Используем expect для автоматического ввода пароля
expect << EOF
set timeout 30
spawn scp "$LOCAL_AGENT" ${SERVER_USER}@${SERVER}:${REMOTE_AGENT_DIR}/
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

expect << EOF
set timeout 30
spawn scp "$LOCAL_ROUTER" ${SERVER_USER}@${SERVER}:${REMOTE_ROUTER_DIR}/
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

expect << EOF
set timeout 30
spawn scp "$LOCAL_REGISTRY" ${SERVER_USER}@${SERVER}:${REMOTE_TMP}/
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

expect << EOF
set timeout 30
spawn scp "$LOCAL_REGISTER_SCRIPT" ${SERVER_USER}@${SERVER}:${REMOTE_TMP}/
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

expect << EOF
set timeout 30
spawn scp "$LOCAL_MAIN_SCRIPT" ${SERVER_USER}@${SERVER}:${REMOTE_TMP}/
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

echo -e "${GREEN}✅ Файлы скопированы${NC}"
echo ""

# Регистрация в SFM
echo -e "${YELLOW}📝 Регистрация в SFM...${NC}"

expect << EOF
set timeout 60
spawn ssh ${SERVER_USER}@${SERVER} "cd ${REMOTE_TMP} && python3 register_crash_detection_in_sfm.py"
expect {
    "password:" {
        send "${SERVER_PASS}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    "Перезаписать?" {
        send "y\r"
        exp_continue
    }
    eof
}
EOF

echo -e "${GREEN}✅ Регистрация в SFM завершена${NC}"
echo ""

# Интеграция в main.py
echo -e "${YELLOW}🔗 Интеграция в main.py...${NC}"

expect << EOF
set timeout 60
spawn ssh ${SERVER_USER}@${SERVER} "cd ${REMOTE_TMP} && python3 add_crash_detection_to_main.py"
expect {
    "password:" {
        send "${SERVER_PASS}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    "Продолжить?" {
        send "y\r"
        exp_continue
    }
    eof
}
EOF

echo -e "${GREEN}✅ Интеграция в main.py завершена${NC}"
echo ""

# Проверка импорта на сервере
echo -e "${YELLOW}🔍 Проверка импорта на сервере...${NC}"

expect << EOF
set timeout 30
spawn ssh ${SERVER_USER}@${SERVER} "cd ${REMOTE_BACKEND} && python3 -c 'from security.ai_agents.crash_detection_agent import CrashDetectionAgent; print(\"✅ Импорт агента успешен\")'"
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

# Проверка router
expect << EOF
set timeout 30
spawn ssh ${SERVER_USER}@${SERVER} "cd ${REMOTE_BACKEND} && python3 -c 'from security.api.routers.crash_detection_router import router; print(\"✅ Импорт router успешен\")'"
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

echo -e "${GREEN}✅ Импорты успешны${NC}"
echo ""

# Статистика SFM
echo -e "${YELLOW}📊 Статистика SFM...${NC}"

# Создаем временный скрипт для статистики
cat > /tmp/check_sfm_stats_crash.py << 'PYEOF'
import json
import sys
sys.path.insert(0, '/opt/aladdin-backend')
with open('/opt/aladdin-backend/data/sfm/function_registry.json', 'r') as f:
    registry = json.load(f)
agents = {k: v for k, v in registry.items() if k not in ['functions', 'handlers', 'last_updated'] and isinstance(v, dict) and 'functions' in v}
total_funcs = sum(len(agent.get('functions', [])) for agent in agents.values())
total_endpoints = sum(len(agent.get('api_endpoints', [])) for agent in agents.values())
print(f'Агентов: {len(agents)}')
print(f'Функций в агентах: {total_funcs}')
print(f'API endpoints: {total_endpoints}')
PYEOF

expect << EOF
set timeout 30
spawn scp /tmp/check_sfm_stats_crash.py ${SERVER_USER}@${SERVER}:${REMOTE_TMP}/
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

expect << EOF
set timeout 30
spawn ssh ${SERVER_USER}@${SERVER} "cd ${REMOTE_TMP} && python3 check_sfm_stats_crash.py"
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

rm -f /tmp/check_sfm_stats_crash.py

echo ""

# Итоговый отчет
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Следующие шаги:${NC}"
echo "1. Проверьте логи сервиса: systemctl status aladdin-backend"
echo "2. Проверьте health endpoint: curl http://localhost:8000/api/crash-detection/health"
echo "3. Перезапустите сервис (если нужно): systemctl restart aladdin-backend"
echo ""
echo -e "${GREEN}🚗 Crash Detection Agent готов к использованию!${NC}"
