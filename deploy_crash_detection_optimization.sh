#!/bin/bash
# Скрипт для деплоя оптимизаций Crash Detection API
# Дата: 6 февраля 2026

set -e  # Остановка при ошибке

echo "🚀 ДЕПЛОЙ ОПТИМИЗАЦИЙ CRASH DETECTION API"
echo "=========================================="

# Конфигурация
SERVER="149.154.65.180"
SERVER_USER="${SSH_USER:-root}"
BACKEND_PATH="/opt/aladdin-backend"
LOCAL_CACHE_FILE="security/api/cache/crash_detection_cache.py"
LOCAL_ROUTER_FILE="crash_detection_router_optimized.py"
REMOTE_CACHE_DIR="$BACKEND_PATH/security/api/cache"
REMOTE_ROUTER_DIR="$BACKEND_PATH/security/api/routers"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}ШАГ 1: Проверка локальных файлов...${NC}"

# Проверка существования файлов
if [ ! -f "$LOCAL_CACHE_FILE" ]; then
    echo -e "${RED}❌ Файл $LOCAL_CACHE_FILE не найден!${NC}"
    exit 1
fi

if [ ! -f "$LOCAL_ROUTER_FILE" ]; then
    echo -e "${RED}❌ Файл $LOCAL_ROUTER_FILE не найден!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Локальные файлы найдены${NC}"

echo -e "${YELLOW}ШАГ 2: Подключение к серверу...${NC}"

# Проверка подключения к серверу
if ! ssh -o ConnectTimeout=5 "$SERVER_USER@$SERVER" "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Не удалось подключиться к серверу $SERVER${NC}"
    echo -e "${YELLOW}💡 Убедитесь, что:${NC}"
    echo "   - SSH ключи настроены"
    echo "   - Сервер доступен"
    echo "   - Переменная SSH_USER установлена (если не root)"
    exit 1
fi

echo -e "${GREEN}✅ Подключение к серверу установлено${NC}"

echo -e "${YELLOW}ШАГ 3: Создание директорий на сервере...${NC}"

ssh "$SERVER_USER@$SERVER" << 'EOF'
    mkdir -p /opt/aladdin-backend/security/api/cache
    mkdir -p /opt/aladdin-backend/security/api/routers
    echo "✅ Директории созданы"
EOF

echo -e "${YELLOW}ШАГ 4: Создание backup существующего роутера...${NC}"

ssh "$SERVER_USER@$SERVER" << EOF
    if [ -f "$REMOTE_ROUTER_DIR/crash_detection_router.py" ]; then
        cp "$REMOTE_ROUTER_DIR/crash_detection_router.py" "$REMOTE_ROUTER_DIR/crash_detection_router.py.backup_\$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backup создан"
    else
        echo "⚠️  Существующий роутер не найден, backup не создан"
    fi
EOF

echo -e "${YELLOW}ШАГ 5: Копирование файлов на сервер...${NC}"

# Копирование модуля кэширования
scp "$LOCAL_CACHE_FILE" "$SERVER_USER@$SERVER:$REMOTE_CACHE_DIR/crash_detection_cache.py"
echo -e "${GREEN}✅ Модуль кэширования скопирован${NC}"

# Копирование оптимизированного роутера
scp "$LOCAL_ROUTER_FILE" "$SERVER_USER@$SERVER:$REMOTE_ROUTER_DIR/crash_detection_router_optimized.py"
echo -e "${GREEN}✅ Оптимизированный роутер скопирован${NC}"

echo -e "${YELLOW}ШАГ 6: Проверка Redis на сервере...${NC}"

ssh "$SERVER_USER@$SERVER" << 'EOF'
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            echo "✅ Redis работает"
        else
            echo "⚠️  Redis установлен, но не запущен"
            echo "   Попытка запуска..."
            systemctl start redis-server 2>/dev/null || service redis start 2>/dev/null || echo "   ❌ Не удалось запустить Redis автоматически"
        fi
    else
        echo "⚠️  Redis не установлен"
        echo "   Установка Redis..."
        apt-get update -qq && apt-get install -y redis-server > /dev/null 2>&1 || \
        yum install -y redis > /dev/null 2>&1 || \
        echo "   ❌ Не удалось установить Redis автоматически"
    fi
EOF

echo -e "${YELLOW}ШАГ 7: Проверка Python зависимостей...${NC}"

ssh "$SERVER_USER@$SERVER" << 'EOF'
    if python3 -c "import redis" 2>/dev/null; then
        echo "✅ Redis Python библиотека установлена"
    else
        echo "⚠️  Установка redis библиотеки..."
        pip3 install redis>=5.0.0 2>/dev/null || echo "   ❌ Не удалось установить автоматически"
    fi
EOF

echo -e "${YELLOW}ШАГ 8: Замена роутера (опционально)...${NC}"

read -p "Заменить существующий роутер на оптимизированный? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ssh "$SERVER_USER@$SERVER" << EOF
        cp "$REMOTE_ROUTER_DIR/crash_detection_router_optimized.py" "$REMOTE_ROUTER_DIR/crash_detection_router.py"
        echo "✅ Роутер заменен"
EOF
    echo -e "${GREEN}✅ Роутер заменен на оптимизированную версию${NC}"
else
    echo -e "${YELLOW}⚠️  Роутер не заменен. Используйте оптимизированный вручную.${NC}"
fi

echo -e "${YELLOW}ШАГ 9: Проверка синтаксиса Python файлов...${NC}"

ssh "$SERVER_USER@$SERVER" << 'EOF'
    python3 -m py_compile /opt/aladdin-backend/security/api/cache/crash_detection_cache.py && \
    python3 -m py_compile /opt/aladdin-backend/security/api/routers/crash_detection_router_optimized.py && \
    echo "✅ Синтаксис Python файлов корректен"
EOF

echo ""
echo -e "${GREEN}=========================================="
echo -e "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo -e "==========================================${NC}"
echo ""
echo -e "${YELLOW}Следующие шаги:${NC}"
echo "1. Перезапустите API Gateway:"
echo "   ssh $SERVER_USER@$SERVER 'systemctl restart aladdin-api-gateway'"
echo "   или"
echo "   ssh $SERVER_USER@$SERVER 'pkill -f uvicorn && cd $BACKEND_PATH && python3 -m uvicorn api_gateway:app --host 0.0.0.0 --port 8002'"
echo ""
echo "2. Запустите тест производительности:"
echo "   python3 test_crash_detection_performance.py"
echo ""
echo "3. Проверьте логи:"
echo "   ssh $SERVER_USER@$SERVER 'tail -f $BACKEND_PATH/logs/api.log | grep crash_detection'"
echo ""
