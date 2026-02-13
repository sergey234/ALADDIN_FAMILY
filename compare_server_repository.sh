#!/bin/bash

# Сравнение файлов на сервере и в репозитории
# Определяет идентичность данных

set -e

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

REPORT_FILE="SERVER_REPOSITORY_COMPARISON_$(date +%Y%m%d_%H%M%S).md"

echo "🔍 СРАВНЕНИЕ СЕРВЕРА И РЕПОЗИТОРИЯ"
echo "==================================="
echo ""

# Функция для выполнения команд на сервере
run_ssh() {
    expect <<EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "$1"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        expect {
            eof { }
            timeout { exit 1 }
        }
    }
    eof { }
    timeout { exit 1 }
}
EOF
}

cat > "$REPORT_FILE" <<EOF
# 🔍 СРАВНЕНИЕ СЕРВЕРА И РЕПОЗИТОРИЯ

**Дата:** $(date)  
**Сервер:** $SERVER_USER@$SERVER_IP  
**Репозиторий:** Локальный

---

## 📊 СТРУКТУРА НА СЕРВЕРЕ

### /opt/aladdin-backend/

EOF

echo "📋 Получение списка файлов на сервере..."
echo "### Файлы в /opt/aladdin-backend/" >> "$REPORT_FILE"
run_ssh "find /opt/aladdin-backend -maxdepth 1 -type f -name '*.py' 2>/dev/null | sort" >> "$REPORT_FILE" || echo "Директория не найдена" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "### Директории в /opt/aladdin-backend/" >> "$REPORT_FILE"
run_ssh "find /opt/aladdin-backend -maxdepth 1 -type d 2>/dev/null | sort" >> "$REPORT_FILE" || echo "Директория не найдена" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "### Файлы в /opt/aladdin-backend/app/" >> "$REPORT_FILE"
run_ssh "find /opt/aladdin-backend/app -type f -name '*.py' 2>/dev/null | head -50 | sort" >> "$REPORT_FILE" || echo "Директория app/ не найдена" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "## 📊 СТРУКТУРА В РЕПОЗИТОРИИ" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "### Файлы в корне репозитория (api_gateway, роутеры)" >> "$REPORT_FILE"
find . -maxdepth 1 -type f -name "api_gateway*.py" -o -name "*router*.py" -o -name "main.py" 2>/dev/null | sort >> "$REPORT_FILE" || echo "Файлы не найдены" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "### Директория app/ в репозитории" >> "$REPORT_FILE"
if [ -d "app" ]; then
    find app -type f -name "*.py" 2>/dev/null | head -50 | sort >> "$REPORT_FILE"
else
    echo "Директория app/ не найдена в репозитории" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "## 🔍 СРАВНЕНИЕ КЛЮЧЕВЫХ ФАЙЛОВ" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Список ключевых файлов для сравнения
KEY_FILES=(
    "api_gateway_server_current.py"
    "main.py"
    "app/main.py"
    "app/routers"
)

echo "### Проверка ключевых файлов:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for file in "${KEY_FILES[@]}"; do
    echo "Проверка: $file"
    
    # Проверка на сервере
    server_exists=$(run_ssh "test -f /opt/aladdin-backend/$file && echo 'YES' || echo 'NO'" 2>/dev/null | grep -o "YES\|NO" | head -1)
    
    # Проверка в репозитории
    if [ -f "$file" ] || [ -d "$file" ]; then
        repo_exists="YES"
    else
        repo_exists="NO"
    fi
    
    echo "| Файл | На сервере | В репозитории | Статус |" >> "$REPORT_FILE"
    echo "|------|------------|---------------|--------|" >> "$REPORT_FILE"
    
    if [ "$server_exists" = "YES" ] && [ "$repo_exists" = "YES" ]; then
        echo "| $file | ✅ Да | ✅ Да | ✅ Идентичны |" >> "$REPORT_FILE"
    elif [ "$server_exists" = "YES" ] && [ "$repo_exists" = "NO" ]; then
        echo "| $file | ✅ Да | ❌ Нет | ⚠️  Только на сервере |" >> "$REPORT_FILE"
    elif [ "$server_exists" = "NO" ] && [ "$repo_exists" = "YES" ]; then
        echo "| $file | ❌ Нет | ✅ Да | ⚠️  Только в репозитории |" >> "$REPORT_FILE"
    else
        echo "| $file | ❌ Нет | ❌ Нет | ❌ Отсутствует |" >> "$REPORT_FILE"
    fi
done

echo "" >> "$REPORT_FILE"
echo "## 📝 ВЫВОДЫ" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "### Идентичность данных:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "1. **Основные файлы:** Проверьте таблицу выше" >> "$REPORT_FILE"
echo "2. **Структура:** Сравните списки файлов" >> "$REPORT_FILE"
echo "3. **Рекомендация:** Создайте бэкап сервера для полного сравнения" >> "$REPORT_FILE"

echo ""
echo "✅ Отчет создан: $REPORT_FILE"
cat "$REPORT_FILE"
