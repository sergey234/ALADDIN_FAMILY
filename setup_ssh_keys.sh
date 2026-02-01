#!/bin/bash

# 🚀 НАСТРОЙКА SSH КЛЮЧЕЙ ДЛЯ АВТОМАТИЗАЦИИ
# Создание ключей и настройка беспарольного доступа

set -e

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
SSH_KEY_PATH="$HOME/.ssh/id_rsa_aladdin"
SSH_CONFIG="$HOME/.ssh/config"

echo "🔐 НАСТРОЙКА SSH КЛЮЧЕЙ"
echo "======================"
echo "Сервер: $SERVER"
echo "Пользователь: $USER"
echo ""

# 1. Проверить существующие ключи
echo "1. 📋 ПРОВЕРКА СУЩЕСТВУЮЩИХ КЛЮЧЕЙ:"
if [ -f "$HOME/.ssh/id_rsa" ]; then
    echo "✅ Найден основной SSH ключ: ~/.ssh/id_rsa"
    SSH_KEY="$HOME/.ssh/id_rsa"
    SSH_PUB_KEY="$HOME/.ssh/id_rsa.pub"
else
    echo "⚠️ Основной SSH ключ не найден, создаем новый"
    SSH_KEY="$SSH_KEY_PATH"
    SSH_PUB_KEY="${SSH_KEY_PATH}.pub"

    # Создать новый ключ
    echo "🔑 Создание нового SSH ключа..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY" -N "" -C "aladdin-deployment-$(date +%Y%m%d)"
    echo "✅ SSH ключ создан: $SSH_KEY"
fi
echo ""

# 2. Проверить доступность сервера
echo "2. 🌐 ПРОВЕРКА ДОСТУПА К СЕРВЕРУ:"
echo "Проверяем подключение к $SERVER..."
if nc -z -w5 $SERVER 22 2>/dev/null; then
    echo "✅ Сервер $SERVER доступен на порту 22"
else
    echo "❌ Сервер $SERVER недоступен"
    exit 1
fi
echo ""

# 3. Скопировать публичный ключ на сервер
echo "3. 📤 КОПИРОВАНИЕ КЛЮЧА НА СЕРВЕР:"
echo "Копируем публичный ключ на сервер..."

# Используем expect для автоматизации ssh-copy-id
/usr/bin/expect -c "
spawn ssh-copy-id -i $SSH_PUB_KEY $USER@$SERVER
expect {
    \"password:\" {
        send \"$PASSWORD\r\"
        expect eof
    }
    \"already exist\" {
        puts \"✅ Ключ уже установлен на сервере\"
        exit 0
    }
    eof {
        puts \"✅ Ключ скопирован на сервер\"
    }
}
"

echo ""

# 4. Тестировать подключение без пароля
echo "4. 🧪 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ:"
echo "Проверяем беспарольное подключение..."
SSH_TEST=$(ssh -i "$SSH_KEY" -o PasswordAuthentication=no -o ConnectTimeout=10 $USER@$SERVER "echo 'SSH ключ работает!'" 2>/dev/null)

if [ "$SSH_TEST" = "SSH ключ работает!" ]; then
    echo "✅ Беспарольное подключение работает!"
else
    echo "❌ Беспарольное подключение не работает"
    echo "Проверяем проблему..."
    ssh -i "$SSH_KEY" -v $USER@$SERVER "echo 'test'" 2>&1 | head -10
    exit 1
fi
echo ""

# 5. Настроить SSH config для удобства (опционально)
echo "5. ⚙️ НАСТРОЙКА SSH CONFIG:"
if [ ! -f "$SSH_CONFIG" ]; then
    touch "$SSH_CONFIG"
fi

if ! grep -q "Host aladdin-server" "$SSH_CONFIG"; then
    echo "" >> "$SSH_CONFIG"
    echo "# ALADDIN Server" >> "$SSH_CONFIG"
    echo "Host aladdin-server" >> "$SSH_CONFIG"
    echo "    HostName $SERVER" >> "$SSH_CONFIG"
    echo "    User $USER" >> "$SSH_CONFIG"
    echo "    IdentityFile $SSH_KEY" >> "$SSH_CONFIG"
    echo "    IdentitiesOnly yes" >> "$SSH_CONFIG"
    echo "✅ SSH config настроен (используйте: ssh aladdin-server)"
else
    echo "ℹ️ SSH config уже настроен"
fi
echo ""

# 6. Финальное тестирование команд
echo "6. 🎯 ТЕСТИРОВАНИЕ КОМАНД:"
echo "Выполняем тестовые команды на сервере..."

# Тест 1: Проверка файла миграции
echo -n "Файл migrate_group3.py: "
RESULT=$(ssh -i "$SSH_KEY" $USER@$SERVER "ls -la /opt/aladdin-backend/migrate_group3.py 2>/dev/null | wc -l")
if [ "$RESULT" -gt 0 ]; then
    echo "✅ Найден"
else
    echo "❌ Не найден"
fi

# Тест 2: Проверка кода Группы 3
echo -n "Код Группы 3 в api_gateway.py: "
RESULT=$(ssh -i "$SSH_KEY" $USER@$SERVER "grep -c 'Группа 3' /opt/aladdin-backend/api_gateway.py 2>/dev/null")
if [ "$RESULT" -gt 0 ]; then
    echo "✅ Найден"
else
    echo "❌ Не найден"
fi

# Тест 3: Health endpoint
echo -n "Health endpoint: "
RESULT=$(ssh -i "$SSH_KEY" $USER@$SERVER "curl -s -w '%{http_code}' http://127.0.0.1:8002/api/health -o /dev/null 2>/dev/null")
if [ "$RESULT" = "200" ]; then
    echo "✅ Работает"
else
    echo "❌ Не отвечает"
fi
echo ""

echo "🎉 SSH КЛЮЧИ НАСТРОЕНЫ УСПЕШНО!"
echo "==============================="
echo ""
echo "📋 ИСПОЛЬЗОВАНИЕ:"
echo "• ssh $USER@$SERVER - беспарольный доступ"
echo "• ssh aladdin-server - через alias (если настроен)"
echo ""
echo "🚀 ТЕПЕРЬ ВСЕ КОМАНДЫ БУДУТ РАБОТАТЬ АВТОМАТИЧЕСКИ!"
echo ""
echo "Пример:"
echo "ssh $USER@$SERVER 'ls -la /opt/aladdin-backend/'"


