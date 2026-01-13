#!/bin/bash

# 🔧 Автоматическая настройка сервера для 42 компонентов
# Использование: ./Scripts/auto_setup_server.sh

set -e

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"
ENDPOINTS_FILE="docs/server/COMPONENTS_API_ENDPOINTS.py"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║     🔧 АВТОМАТИЧЕСКАЯ НАСТРОЙКА СЕРВЕРА ДЛЯ 42 КОМПОНЕНТОВ                  ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Проверка файла
if [ ! -f "$ENDPOINTS_FILE" ]; then
    echo -e "${RED}❌${NC} Файл $ENDPOINTS_FILE не найден!"
    exit 1
fi

echo -e "${GREEN}✅${NC} Файл найден: $ENDPOINTS_FILE"
echo ""

# Попытка подключения и настройки
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 Подключение к серверу..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Создаем временный скрипт для выполнения на сервере
cat > /tmp/setup_components_server.sh << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

echo "🔍 Поиск главного файла FastAPI..."

# Возможные пути к главному файлу
POSSIBLE_PATHS=(
    "/root/main.py"
    "/root/app.py"
    "/root/server.py"
    "/root/security/api/main.py"
    "/root/security/api/app.py"
    "/root/api/main.py"
    "/root/api/app.py"
)

MAIN_FILE=""
for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        MAIN_FILE="$path"
        echo "✅ Найден главный файл: $MAIN_FILE"
        break
    fi
done

if [ -z "$MAIN_FILE" ]; then
    echo "⚠️ Главный файл не найден в стандартных местах"
    echo "Поиск файлов FastAPI..."
    find /root -name "main.py" -o -name "app.py" 2>/dev/null | head -5
    echo ""
    echo "Пожалуйста, укажите путь к главному файлу вручную"
    exit 1
fi

# Создаем директорию для роутеров, если не существует
ROUTER_DIR="/root/security/api/routers"
if [ ! -d "$ROUTER_DIR" ]; then
    echo "📁 Создание директории для роутеров: $ROUTER_DIR"
    mkdir -p "$ROUTER_DIR"
fi

# Копируем файл роутера
if [ -f "/tmp/components_router.py" ]; then
    echo "📋 Копирование роутера..."
    cp /tmp/components_router.py "$ROUTER_DIR/components_router.py"
    echo "✅ Роутер скопирован: $ROUTER_DIR/components_router.py"
else
    echo "❌ Файл /tmp/components_router.py не найден"
    exit 1
fi

# Проверяем, не добавлен ли уже router
if grep -q "components_router" "$MAIN_FILE"; then
    echo "⚠️ Router уже зарегистрирован в $MAIN_FILE"
else
    echo "📝 Добавление router в $MAIN_FILE..."
    
    # Создаем backup
    cp "$MAIN_FILE" "${MAIN_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
    
    # Добавляем импорт и регистрацию router
    # Ищем место после других импортов
    if grep -q "from.*router import" "$MAIN_FILE"; then
        # Добавляем после последнего импорта router
        sed -i '/from.*router import/a from security.api.routers.components_router import router as components_router' "$MAIN_FILE"
    else
        # Добавляем в конец импортов
        sed -i '/^from fastapi import/a from security.api.routers.components_router import router as components_router' "$MAIN_FILE"
    fi
    
    # Добавляем регистрацию router
    if grep -q "app.include_router" "$MAIN_FILE"; then
        # Добавляем после последнего include_router
        sed -i '/app.include_router/a app.include_router(components_router)' "$MAIN_FILE"
    else
        # Добавляем после создания app
        sed -i '/app = FastAPI/a app.include_router(components_router)' "$MAIN_FILE"
    fi
    
    echo "✅ Router добавлен в $MAIN_FILE"
fi

# Создаем SQL скрипт для таблиц
cat > /tmp/create_component_tables.sql << 'SQL_SCRIPT'
-- Таблица статусов компонентов
CREATE TABLE IF NOT EXISTS component_status (
    id SERIAL PRIMARY KEY,
    component_id VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(component_id, user_id)
);

-- Таблица конфигураций компонентов
CREATE TABLE IF NOT EXISTS component_configuration (
    id SERIAL PRIMARY KEY,
    component_id VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    settings JSONB DEFAULT '{}',
    version VARCHAR(50) DEFAULT '1.0.0',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(component_id, user_id)
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_component_status_user ON component_status(user_id);
CREATE INDEX IF NOT EXISTS idx_component_config_user ON component_configuration(user_id);
SQL_SCRIPT

echo "📊 SQL скрипт создан: /tmp/create_component_tables.sql"
echo "⚠️ Выполните SQL скрипт вручную в вашей БД"

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Выполните SQL скрипт: /tmp/create_component_tables.sql"
echo "2. Перезапустите сервер"
echo "3. Протестируйте endpoints"
REMOTE_SCRIPT

chmod +x /tmp/setup_components_server.sh

# Копируем файл endpoints на сервер
echo "📤 Копирование файла endpoints на сервер..."
if command -v sshpass &> /dev/null; then
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$ENDPOINTS_FILE" "${SERVER_USER}@${SERVER_IP}:/tmp/components_router.py"
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/setup_components_server.sh "${SERVER_USER}@${SERVER_IP}:/tmp/setup_components_server.sh"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} Файлы скопированы на сервер"
        echo ""
        echo "🚀 Запуск настройки на сервере..."
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "bash /tmp/setup_components_server.sh"
    else
        echo -e "${RED}❌${NC} Не удалось скопировать файлы"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️${NC} sshpass не установлен"
    echo ""
    echo "Выполните вручную:"
    echo "1. scp $ENDPOINTS_FILE ${SERVER_USER}@${SERVER_IP}:/tmp/components_router.py"
    echo "2. ssh ${SERVER_USER}@${SERVER_IP}"
    echo "3. Выполните команды из /tmp/setup_components_server.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ НАСТРОЙКА ЗАВЕРШЕНА!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

