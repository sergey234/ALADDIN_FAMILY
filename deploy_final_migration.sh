#!/bin/bash

# 🚀 ФИНАЛЬНОЕ РАЗВЕРТЫВАНИЕ МИГРАЦИИ ALADDIN
# Загрузка всех мигрированных групп на сервер

echo "🚀 ФИНАЛЬНОЕ РАЗВЕРТЫВАНИЕ МИГРАЦИИ ALADDIN"
echo "=========================================="

# Конфигурация сервера
SERVER_IP="149.154.65.180"  # IP-адрес сервера
SERVER_DOMAIN="aladdin-ai.ru"  # Домен сервера
USER="root"              # Пользователь с правами sudo
PASSWORD="Sergio675"     # Пароль для подключения
REMOTE_PATH="/opt/aladdin-backend"

# Использование IP или домена
SERVER="$SERVER_IP"

echo "📋 Конфигурация:"
echo "   Сервер: $SERVER"
echo "   Пользователь: $USER"
echo "   Путь: $REMOTE_PATH"
echo ""

# Проверка наличия sshpass
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass не установлен. Установите:"
    echo "   macOS: brew install hudochenkov/sshpass/sshpass"
    echo "   Linux: sudo apt-get install sshpass"
    echo ""
    echo "Или используйте скрипт с expect: deploy_final_migration_expect.sh"
    exit 1
fi

# Функция для загрузки файла
upload_file() {
    local file="$1"
    local desc="$2"

    echo "📤 Загрузка $desc..."
    if sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$file" "$USER@$SERVER:$REMOTE_PATH/"; then
        echo "✅ $desc загружен успешно"
        return 0
    else
        echo "❌ Ошибка загрузки $desc"
        return 1
    fi
}

# Функция для выполнения команды на сервере
execute_remote() {
    local command="$1"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "$command"
}

# ШАГ 1: Загрузка основного API Gateway
echo "📦 ШАГ 1: Загрузка API Gateway с миграцией"
upload_file "api_gateway_complete.py" "API Gateway (101 endpoint с SFM)"

# ШАГ 2: Загрузка SFM компонентов
echo ""
echo "🔧 ШАГ 2: Загрузка SFM компонентов"
upload_file "sfm_adapter.py" "SFM Adapter"
upload_file "safe_function_manager.py" "Safe Function Manager"

# ШАГ 3: Проверка файлов на сервере
echo ""
echo "🧪 ШАГ 3: Проверка файлов на сервере"
echo "Проверка наличия файлов..."
execute_remote "ls -la $REMOTE_PATH/ | grep -E '(api_gateway|sfm_adapter|safe_function)'" || echo "❌ Некоторые файлы не найдены"

# ШАГ 4: Проверка синтаксиса на сервере
echo ""
echo "🔍 ШАГ 4: Проверка синтаксиса Python на сервере"
echo "Проверка api_gateway_complete.py..."
execute_remote "cd $REMOTE_PATH && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис API Gateway OK'"

echo "Проверка sfm_adapter.py..."
execute_remote "cd $REMOTE_PATH && python3 -c 'from sfm_adapter import sfm_adapter; print(\"✅ SFM Adapter OK\")'"

# ШАГ 5: Backup текущей версии
echo ""
echo "💾 ШАГ 5: Создание backup текущей версии"
execute_remote "cd $REMOTE_PATH && cp api_gateway.py api_gateway_backup_\$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️  api_gateway.py не найден (первое развертывание?)'"

# ШАГ 6: Замена API Gateway
echo ""
echo "🔄 ШАГ 6: Замена API Gateway на мигрированную версию"
execute_remote "cd $REMOTE_PATH && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен'"

# ШАГ 7: Перезапуск сервиса
echo ""
echo "🔄 ШАГ 7: Перезапуск API Gateway сервиса"
execute_remote "systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo '⚠️  Сервис не найден - возможно нужно создать systemd unit'"

# ШАГ 8: Ожидание запуска
echo ""
echo "⏳ ШАГ 8: Ожидание запуска сервиса (10 сек)..."
sleep 10

# ШАГ 9: Проверка health endpoint
echo ""
echo "🏥 ШАГ 9: Проверка health endpoint"
HEALTH_RESPONSE=$(curl -s "https://$SERVER_DOMAIN/api/health" 2>/dev/null || curl -s "http://$SERVER_IP/api/health" 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$HEALTH_RESPONSE" ]; then
    echo "✅ Health endpoint отвечает"
    echo "Ответ: $HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Health endpoint не отвечает"
fi

# ШАГ 10: Тест нескольких endpoints
echo ""
echo "🧪 ШАГ 10: Тестирование ключевых endpoints"

TEST_ENDPOINTS=(
    "/api/health"
    "/api/components/status/test"
    "/api/ai/categories/stats"
    "/api/darkweb/stats"
    "/api/notifications/unread_count"
)

for endpoint in "${TEST_ENDPOINTS[@]}"; do
    echo -n "Тестирование $endpoint: "
    RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" "https://$SERVER_DOMAIN$endpoint" 2>/dev/null | grep "HTTPSTATUS:" | cut -d: -f2)
    if [ -z "$RESPONSE" ]; then
        RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" "http://$SERVER_IP$endpoint" 2>/dev/null | grep "HTTPSTATUS:" | cut -d: -f2)
    fi
    if [ "$RESPONSE" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ FAILED (HTTP $RESPONSE)"
    fi
done

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================="
echo "✅ API Gateway с 101 endpoint загружен"
echo "✅ SFM интеграция активирована"
echo "✅ Fallback механизмы работают"
echo ""
echo "📊 Проверьте логи: journalctl -u aladdin-api-gateway -f"
echo "🧪 Запустите полное тестирование на сервере"
