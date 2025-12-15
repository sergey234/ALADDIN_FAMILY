#!/bin/bash
# -*- coding: utf-8 -*-

# Скрипт для деплоя Roadside Assistance Agent на сервер
# Использование: ./deploy_roadside_assistance_to_server.sh

SERVER="root@149.154.65.180"
SERVER_PASSWORD="Sergio675"
REMOTE_BASE="/opt/aladdin-backend"

echo "🚀 Деплой Roadside Assistance Agent на сервер"
echo ""

# Файлы для копирования
FILES=(
    "security/ai_agents/roadside_assistance_agent.py"
    "security/api/routers/roadside_assistance_router.py"
    "security/ai_agents/function_registry_entry_roadside_assistance.json"
    "register_roadside_assistance_in_sfm.py"
    "add_roadside_assistance_to_main.py"
)

# Копирование файлов
echo "📤 Копирование файлов на сервер..."
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⚠️  Файл не найден: $file"
        continue
    fi

    # Определение целевого пути
    if [[ "$file" == security/ai_agents/*.py ]]; then
        TARGET="${REMOTE_BASE}/security/ai_agents/$(basename $file)"
    elif [[ "$file" == security/api/routers/*.py ]]; then
        TARGET="${REMOTE_BASE}/security/api/routers/$(basename $file)"
    elif [[ "$file" == security/ai_agents/*.json ]]; then
        TARGET="${REMOTE_BASE}/security/ai_agents/$(basename $file)"
    else
        TARGET="${REMOTE_BASE}/$(basename $file)"
    fi

    echo "  📄 $file → $TARGET"
    expect << EOF
spawn scp "$file" ${SERVER}:${TARGET}
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF
done

echo ""
echo "✅ Файлы скопированы"
echo ""

# Регистрация в SFM
echo "📝 Регистрация в SFM..."
expect << EOF
spawn ssh ${SERVER} "cd ${REMOTE_BASE} && /opt/aladdin-backend/venv/bin/python3 register_roadside_assistance_in_sfm.py"
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

echo ""
echo "✅ Регистрация в SFM завершена"
echo ""

# Интеграция в main.py
echo "🔗 Интеграция в main.py..."
expect << EOF
spawn ssh ${SERVER} "cd ${REMOTE_BASE} && /opt/aladdin-backend/venv/bin/python3 add_roadside_assistance_to_main.py"
expect {
    "password:" {
        send "${SERVER_PASSWORD}\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF

echo ""
echo "✅ Интеграция в main.py завершена"
echo ""
echo "🎉 Деплой завершен!"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Проверить синтаксис main.py на сервере"
echo "   2. Перезапустить сервис: systemctl restart aladdin-backend"
echo "   3. Проверить health endpoint: curl http://localhost:8000/api/roadside-assistance/health"
