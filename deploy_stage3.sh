#!/bin/bash

# Скрипт для загрузки всех router'ов Этапа 3 на сервер
# Использование: ./deploy_stage3.sh

set -e

SERVER="149.154.65.180"
USERNAME="root"
PASSWORD="Sergio675"
REMOTE_BACKEND="/opt/aladdin-backend"
REMOTE_ROUTERS="$REMOTE_BACKEND/security/api/routers"

echo "🚀 ЗАГРУЗКА ЭТАПА 3: ОПЦИОНАЛЬНО (13 endpoint'ов) НА СЕРВЕР"
echo "============================================================"
echo ""

# Список файлов для загрузки
FILES=(
    "offline_storage_sync_router.py"
    "crash_detection_sync_router.py"
    "elderly_interface_sync_router.py"
)

# Проверка наличия файлов
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Ошибка: файл $file не найден!"
        exit 1
    fi
done

echo "✅ Все файлы найдены"
echo ""

# Загрузка каждого router'а
for file in "${FILES[@]}"; do
    echo "📤 Загружаю $file..."
    expect -c "
set timeout 90
set password \"$PASSWORD\"
set server \"$USERNAME@$SERVER\"
spawn scp $file \$server:$REMOTE_ROUTERS/$file
expect {
    \"password:\" {
        send \"\$password\\r\"
        expect {
            \"100%\" {
                puts \"✅ $file загружен успешно\"
            }
            eof {
                puts \"✅ $file загружен (завершено)\"
            }
        }
    }
    \"yes/no\" {
        send \"yes\\r\"
        expect \"password:\"
        send \"\$password\\r\"
        expect {
            \"100%\" {
                puts \"✅ $file загружен успешно\"
            }
            eof {
                puts \"✅ $file загружен (завершено)\"
            }
        }
    }
    eof {
        puts \"⚠️  Возможная ошибка при загрузке $file\"
    }
    timeout {
        puts \"❌ Таймаут при загрузке $file\"
    }
}
"
    
    if [ $? -eq 0 ]; then
        echo "✅ $file загружен на сервер"
    else
        echo "❌ Ошибка при загрузке $file"
        exit 1
    fi
    echo ""
done

# Обновление main.py
echo "🔄 Обновляю main.py на сервере..."
expect -c "
set timeout 90
set password \"$PASSWORD\"
set server \"$USERNAME@$SERVER\"
spawn scp main.py.server \$server:$REMOTE_BACKEND/main.py
expect {
    \"password:\" {
        send \"\$password\\r\"
        expect {
            \"100%\" {
                puts \"✅ main.py обновлен\"
            }
            eof {
                puts \"✅ main.py обновлен (завершено)\"
            }
        }
    }
    \"yes/no\" {
        send \"yes\\r\"
        expect \"password:\"
        send \"\$password\\r\"
        expect {
            \"100%\" {
                puts \"✅ main.py обновлен\"
            }
            eof {
                puts \"✅ main.py обновлен (завершено)\"
            }
        }
    }
    eof {
        puts \"⚠️  Возможная ошибка\"
    }
    timeout {
        puts \"❌ Таймаут\"
    }
}
"

if [ $? -eq 0 ]; then
    echo "✅ main.py обновлен на сервере"
else
    echo "❌ Ошибка при обновлении main.py"
    exit 1
fi

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
echo "✅ ЗАГРУЗКА ЭТАПА 3 ЗАВЕРШЕНА"
echo ""
echo "📋 Загружено router'ов: ${#FILES[@]}"
echo "📋 Следующие шаги:"
echo "1. Проверьте логи: ssh $USERNAME@$SERVER 'journalctl -u aladdin-main-api-gateway -n 50'"
echo "2. Протестируйте endpoint'ы"
