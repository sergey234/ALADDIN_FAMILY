#!/bin/bash

# Скрипт для настройки API ключей (или Mock режима) для Identity Theft
# Этот скрипт создает .env файл с заглушками для демонстрации работы

ENV_FILE="/opt/aladdin-backend/.env"

echo "🔧 Настройка Identity Theft API..."

# Проверка наличия .env файла
sshpass -p "Sergio675" ssh -o StrictHostKeyChecking=no root@149.154.65.180 << 'EOF'
if [ ! -f /opt/aladdin-backend/.env ]; then
    echo "📄 Создание .env файла..."
    touch /opt/aladdin-backend/.env
fi

# Добавление настроек для Identity Theft (Mock Mode)
# Мы используем режим симуляции, чтобы убрать ошибку 503
if ! grep -q "IDENTITY_THEFT_MOCK_MODE" /opt/aladdin-backend/.env; then
    echo "IDENTITY_THEFT_MOCK_MODE=true" >> /opt/aladdin-backend/.env
    echo "✅ Mock режим для Identity Theft включен"
else
    sed -i 's/IDENTITY_THEFT_MOCK_MODE=.*/IDENTITY_THEFT_MOCK_MODE=true/' /opt/aladdin-backend/.env
    echo "✅ Mock режим для Identity Theft обновлен"
fi

# Добавление настроек для Data Cleanup (Mock Mode)
if ! grep -q "DATA_CLEANUP_MOCK_MODE" /opt/aladdin-backend/.env; then
    echo "DATA_CLEANUP_MOCK_MODE=true" >> /opt/aladdin-backend/.env
    echo "✅ Mock режим для Data Cleanup включен"
else
    sed -i 's/DATA_CLEANUP_MOCK_MODE=.*/DATA_CLEANUP_MOCK_MODE=true/' /opt/aladdin-backend/.env
    echo "✅ Mock режим для Data Cleanup обновлен"
fi

# Перезапуск сервиса
echo "🔄 Перезапуск API Gateway..."
systemctl restart aladdin-main-api-gateway
sleep 5
EOF

echo "✅ Настройка завершена!"
