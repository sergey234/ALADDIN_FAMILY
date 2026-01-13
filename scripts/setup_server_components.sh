#!/bin/bash

# 🔧 Скрипт для настройки сервера для 42 компонентов
# Использование: ./Scripts/setup_server_components.sh

set -e

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║     🔧 НАСТРОЙКА СЕРВЕРА ДЛЯ 42 КОМПОНЕНТОВ                                  ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Сервер: ${SERVER_USER}@${SERVER_IP}"
echo ""

# Проверка наличия sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}⚠️${NC} sshpass не установлен. Устанавливаю..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        sudo apt-get install -y sshpass
    fi
fi

# Проверка наличия файла с endpoints
ENDPOINTS_FILE="docs/server/COMPONENTS_API_ENDPOINTS.py"
if [ ! -f "$ENDPOINTS_FILE" ]; then
    echo -e "${RED}❌${NC} Файл $ENDPOINTS_FILE не найден!"
    exit 1
fi

echo -e "${GREEN}✅${NC} Файл с endpoints найден: $ENDPOINTS_FILE"
echo ""

# Инструкции для ручной настройки
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Подключитесь к серверу:"
echo "   ${GREEN}ssh ${SERVER_USER}@${SERVER_IP}${NC}"
echo "   Пароль: ${SERVER_PASSWORD}"
echo ""
echo "2. Найдите главный файл FastAPI (обычно main.py или app.py)"
echo ""
echo "3. Скопируйте файл COMPONENTS_API_ENDPOINTS.py на сервер:"
echo "   ${GREEN}scp ${ENDPOINTS_FILE} ${SERVER_USER}@${SERVER_IP}:/root/security/api/routers/components_router.py${NC}"
echo ""
echo "4. Зарегистрируйте router в главном app:"
echo "   Добавьте в main.py или app.py:"
echo "   ${GREEN}from security.api.routers.components_router import router as components_router${NC}"
echo "   ${GREEN}app.include_router(components_router)${NC}"
echo ""
echo "5. Создайте таблицы в БД (см. docs/ИНСТРУКЦИЯ_ПО_НАСТРОЙКЕ_СЕРВЕРА_КОМПОНЕНТОВ.md)"
echo ""
echo "6. Перезапустите сервер"
echo ""
echo "7. Протестируйте endpoints:"
echo "   ${GREEN}curl -X GET \"https://aladdin-ai.ru/api/components/status/crash_detection_agent\"${NC}"
echo ""

# Попытка автоматической настройки (если возможно)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 АВТОМАТИЧЕСКАЯ НАСТРОЙКА (опционально):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Попытаться автоматически скопировать файл на сервер? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Копирование файла на сервер..."
    sshpass -p "$SERVER_PASSWORD" scp "$ENDPOINTS_FILE" "${SERVER_USER}@${SERVER_IP}:/tmp/components_router.py"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} Файл скопирован на сервер в /tmp/components_router.py"
        echo ""
        echo "Теперь на сервере выполните:"
        echo "  1. Переместите файл: ${GREEN}mv /tmp/components_router.py /root/security/api/routers/${NC}"
        echo "  2. Зарегистрируйте router в главном app"
        echo "  3. Создайте таблицы в БД"
        echo "  4. Перезапустите сервер"
    else
        echo -e "${RED}❌${NC} Не удалось скопировать файл. Выполните копирование вручную."
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 ДОКУМЕНТАЦИЯ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Полная инструкция: ${GREEN}docs/ИНСТРУКЦИЯ_ПО_НАСТРОЙКЕ_СЕРВЕРА_КОМПОНЕНТОВ.md${NC}"
echo ""
echo "Файл с endpoints: ${GREEN}${ENDPOINTS_FILE}${NC}"
echo ""

