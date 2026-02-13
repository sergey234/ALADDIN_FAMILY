#!/bin/bash

# Скрипт для загрузки Parental Control Sync Router на сервер
# Использование: ./deploy_parental_control.sh

set -e

SERVER="149.154.65.180"
USERNAME="root"
PASSWORD="Sergio675"
REMOTE_BACKEND="/opt/aladdin-backend"
REMOTE_ROUTERS="$REMOTE_BACKEND/security/api/routers"

echo "🚀 ЗАГРУЗКА PARENTAL CONTROL SYNC ROUTER НА СЕРВЕР"
echo "=================================================="
echo ""

# Проверка наличия файлов
if [ ! -f "parental_control_sync_router.py" ]; then
    echo "❌ Ошибка: файл parental_control_sync_router.py не найден!"
    exit 1
fi

if [ ! -f "main.py.server" ]; then
    echo "❌ Ошибка: файл main.py.server не найден!"
    exit 1
fi

echo "✅ Файлы найдены"
echo ""

# Загрузка router'а
echo "📤 Загружаю parental_control_sync_router.py..."
expect -c "
set timeout 90
set password \"$PASSWORD\"
set server \"$USERNAME@$SERVER\"
spawn scp parental_control_sync_router.py \$server:$REMOTE_ROUTERS/parental_control_sync_router.py
expect {
    \"password:\" {
        send \"\$password\\r\"
        expect {
            \"100%\" {
                puts \"✅ Router загружен успешно\"
            }
            eof {
                puts \"✅ Router загружен (завершено)\"
            }
        }
    }
    \"yes/no\" {
        send \"yes\\r\"
        expect \"password:\"
        send \"\$password\\r\"
        expect {
            \"100%\" {
                puts \"✅ Router загружен успешно\"
            }
            eof {
                puts \"✅ Router загружен (завершено)\"
            }
        }
    }
    eof {
        puts \"⚠️  Возможная ошибка при загрузке\"
    }
    timeout {
        puts \"❌ Таймаут при загрузке\"
    }
}
"

if [ $? -eq 0 ]; then
    echo "✅ Router загружен на сервер"
else
    echo "❌ Ошибка при загрузке router'а"
    exit 1
fi

echo ""

# Проверка и обновление main.py на сервере
echo "🔄 Проверяю main.py на сервере..."
expect -c "
set timeout 90
set password \"$PASSWORD\"
set server \"$USERNAME@$SERVER\"
spawn ssh -o StrictHostKeyChecking=no \$server \"grep -q 'parental_control_sync_router' $REMOTE_BACKEND/main.py 2>/dev/null && echo 'EXISTS' || echo 'NOT_FOUND'\"
expect {
    \"password:\" {
        send \"\$password\\r\"
        expect {
            \"EXISTS\" {
                puts \"✅ Router уже подключен в main.py\"
            }
            \"NOT_FOUND\" {
                puts \"⚠️  Router не найден в main.py, нужно добавить вручную\"
            }
            eof {
                puts \"⚠️  Не удалось проверить main.py\"
            }
        }
    }
    \"yes/no\" {
        send \"yes\\r\"
        expect \"password:\"
        send \"\$password\\r\"
        expect {
            \"EXISTS\" {
                puts \"✅ Router уже подключен в main.py\"
            }
            \"NOT_FOUND\" {
                puts \"⚠️  Router не найден в main.py, нужно добавить вручную\"
            }
            eof {
                puts \"⚠️  Не удалось проверить main.py\"
            }
        }
    }
    eof {
        puts \"⚠️  Не удалось подключиться к серверу\"
    }
    timeout {
        puts \"❌ Таймаут при проверке\"
    }
}
"

echo ""

# Перезапуск сервиса
echo "🔄 Перезапускаю сервис FastAPI..."
expect -c "
set timeout 90
set password \"$PASSWORD\"
set server \"$USERNAME@$SERVER\"
spawn ssh -o StrictHostKeyChecking=no \$server \"systemctl restart aladdin-main-api-gateway && echo 'RESTARTED' || echo 'ERROR'\"
expect {
    \"password:\" {
        send \"\$password\\r\"
        expect {
            \"RESTARTED\" {
                puts \"✅ Сервис перезапущен\"
            }
            \"ERROR\" {
                puts \"❌ Ошибка при перезапуске сервиса\"
            }
            eof {
                puts \"⚠️  Команда выполнена\"
            }
        }
    }
    \"yes/no\" {
        send \"yes\\r\"
        expect \"password:\"
        send \"\$password\\r\"
        expect {
            \"RESTARTED\" {
                puts \"✅ Сервис перезапущен\"
            }
            \"ERROR\" {
                puts \"❌ Ошибка при перезапуске сервиса\"
            }
            eof {
                puts \"⚠️  Команда выполнена\"
            }
        }
    }
    eof {
        puts \"⚠️  Не удалось подключиться к серверу\"
    }
    timeout {
        puts \"❌ Таймаут при перезапуске\"
    }
}
"

echo ""
echo "✅ ЗАГРУЗКА ЗАВЕРШЕНА"
echo ""
echo "📋 Следующие шаги:"
echo "1. Проверьте логи сервиса: ssh $USERNAME@$SERVER 'journalctl -u aladdin-main-api-gateway -n 50 | grep -i parental'"
echo "2. Протестируйте endpoint'ы: ./test_parental_control_api.sh http://$SERVER:8000 family_001 child_123"
