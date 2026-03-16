#!/bin/bash
# Развертывание через SSH с использованием heredoc
# Использование: ./deploy_via_ssh.sh

SERVER="149.154.65.180"
USER="root"
REMOTE_DIR="/opt/aladdin-backend"

echo "============================================================"
echo "РАЗВЕРТЫВАНИЕ МИГРАЦИИ НА СЕРВЕРЕ"
echo "============================================================"
echo ""

# Копируем файлы
echo "📤 Копирование файлов..."
scp -o StrictHostKeyChecking=no create_component_tables.sql apply_migration.py test_endpoints.py verify_endpoints.py EXECUTE_ON_SERVER.sh ${USER}@${SERVER}:${REMOTE_DIR}/app/database/migrations/ 2>&1 | grep -v "password" || echo "Файлы скопированы (требуется пароль)"

echo ""
echo "🔧 Выполнение команд на серH'
cd /opt/aladdin-backend
echo "Текущая директория: $(pwd)"
echo ""

echo "============================================================"
echo "ШАГ 1: Применение миграции"
echo "============================================================"
python3 app/database/migrations/apply_migration.py

echo ""
echo "============================================================"
echo "ШАГ 2: Тестирование endpoints"
echo "============================================================"
export API_BASE_URL="https://aladdin-ai.ru"
python3 app/database/migrations/test_endpoints.py

echo ""
echo "============================================================"
echo "ШАГ 3: Проверка документации"
echo "============================================================"
python3 app/database/migrations/verify_endpoints.py

echo ""
echo "============================================================"
echo "✅ ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ"
echo "=============="
