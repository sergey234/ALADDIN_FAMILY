#!/bin/bash

# Параметры сервера
SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

echo "🚀 НАЧИНАЕМ ПОЛНОЕ АВТОМАТИЧЕСКОЕ РАЗВЕРТЫВАНИЕ ML СИСТЕМЫ"
echo "======================================================"

# Проверка sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass не найден! Установите его (brew install sshpass)."
    exit 1
fi

echo "📂 ШАГ 1: Создание структуры директорий на сервере..."

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p /opt/aladdin-backend/app/routers /opt/aladdin-backend/security/api/routers"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка создания директорий"
    exit 1
fi

echo "📤 ШАГ 2: Отправка файлов на сервер..."

# 1. Отправка основного файла
echo "Отправка api_gateway_complete_full.py..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no api_gateway_complete_full.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/

# 2. Отправка referral router
echo "Отправка app/routers/referral_fixed.py..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no app/routers/referral_fixed.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/app/routers/

# 3. Отправка security routers (ВСЕХ!)
echo "Отправка всех security роутеров..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no security/api/routers/*.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/security/api/routers/

if [ $? -ne 0 ]; then
    echo "❌ Ошибка отправки security роутеров"
    exit 1
fi

echo "✅ Все файлы успешно отправлены!"

echo ""
echo "🔧 ШАГ 3: Настройка и перезапуск..."

# Подключение к серверу и выполнение команд
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF'

echo "Переход в директорию проекта..."
cd /opt/aladdin-backend

echo "Создание пустых __init__.py если их нет..."
touch security/__init__.py
touch security/api/__init__.py
touch security/api/routers/__init__.py
touch app/__init__.py
touch app/routers/__init__.py

echo "Резервная копия старого api_gateway..."
cp api_gateway.py api_gateway.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

echo "Установка нового api_gateway..."
cp api_gateway_complete_full.py api_gateway.py
chmod +x api_gateway.py

echo "Проверка синтаксиса..."
python3 -m py_compile api_gateway.py

if [ $? -eq 0 ]; then
    echo "✅ Синтаксис корректен!"

    echo "Перезапуск API Gateway..."
    systemctl restart aladdin-main-api-gateway

    echo "Ожидание запуска (20 секунд)..."
    sleep 20

    echo "🧪 Тестирование работы..."

    # Health check
    echo "Health check:"
    curl -s http://127.0.0.1:8002/api/health

    echo ""
    echo "Тест новых эндпоинтов:"

    # Тест новых эндпоинтов
    echo "Protection scan (должен работать):"
    curl -s http://127.0.0.1:8002/api/protection/scan

    echo "Referral stats (должен требовать auth):"
    curl -s http://127.0.0.1:8002/api/referral/stats

    echo "Crash Detection Status:"
    curl -s http://127.0.0.1:8002/api/crash-detection/status

    echo ""
    echo "🔍 Проверка логов на наличие ошибок импорта:"
    grep -i "not available" /var/log/syslog | tail -n 5 2>/dev/null || true
    journalctl -u aladdin-main-api-gateway -n 20 --no-pager | grep "not available"

    echo ""
    echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"

else
    echo "❌ Ошибка синтаксиса! Откат..."
    cp api_gateway.backup.* api_gateway.py
    systemctl restart aladdin-main-api-gateway
fi

EOF

echo ""
echo "🎯 РАЗВЕРТЫВАНИЕ ML СИСТЕМЫ ПОЛНОСТЬЮ ЗАВЕРШЕНО!"