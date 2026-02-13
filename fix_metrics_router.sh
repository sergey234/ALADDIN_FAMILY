#!/bin/bash

# 🔧 СКРИПТ ИСПРАВЛЕНИЯ METRICS ROUTER НА СЕРВЕРЕ
# Дата: 2026-02-13
# Цель: Исправить подключение metrics_router для продакшн

echo "=== ИСПРАВЛЕНИЕ METRICS ROUTER НА СЕРВЕРЕ ==="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MAIN_PY="/opt/aladdin-backend/main.py"
BACKUP_FILE="${MAIN_PY}.backup_$(date +%Y%m%d_%H%M%S)"

# 1. Создание резервной копии
echo "1️⃣ Создание резервной копии main.py..."
cp "$MAIN_PY" "$BACKUP_FILE"
echo -e "${GREEN}✅ Резервная копия создана: $BACKUP_FILE${NC}"

# 2. Проверка текущего подключения
echo ""
echo "2️⃣ Проверка текущего подключения..."
if grep -q "if metrics_router_available:" "$MAIN_PY"; then
    echo -e "${GREEN}✅ Роутер уже подключен${NC}"
    
    # Проверяем, независим ли он
    if grep -B 5 "if metrics_router_available:" "$MAIN_PY" | grep -q "if system_router_available:"; then
        echo -e "${YELLOW}⚠️ Роутер подключен условно (зависит от system_router)${NC}"
        echo "   Исправляем..."
        
        # Создаем временный файл с исправлением
        python3 << 'PYTHON_SCRIPT'
import re

main_py_path = "/opt/aladdin-backend/main.py"

# Читаем файл
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем блок с metrics_router внутри system_router
pattern = r'(if system_router_available:.*?)(\s+if metrics_router_available:.*?app\.include_router\(metrics_router\).*?\n)'

def fix_metrics_router(match):
    system_block = match.group(1)
    metrics_block = match.group(2)
    
    # Убираем отступы из metrics_block и делаем его независимым
    metrics_independent = re.sub(r'^\s+', '', metrics_block, flags=re.MULTILINE)
    
    # Возвращаем system_block и независимый metrics_block
    return system_block + metrics_independent

# Заменяем
new_content = re.sub(pattern, fix_metrics_router, content, flags=re.DOTALL)

# Если не нашлось, добавляем независимый блок после system_router
if "if metrics_router_available:" not in new_content or new_content == content:
    # Ищем место после system_router
    system_pattern = r'(if system_router_available:.*?print\([^)]+\)\s*\n)'
    
    def add_independent_metrics(match):
        return match.group(0) + "\nif metrics_router_available:\n    try:\n        app.include_router(metrics_router)\n        print(\"✅ Роутер Metrics подключен\")\n    except Exception as e:\n        print(f\"❌ Ошибка подключения Metrics: {e}\")\n"
    
    new_content = re.sub(system_pattern, add_independent_metrics, new_content, flags=re.DOTALL)

# Записываем обратно
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Файл исправлен")
PYTHON_SCRIPT

    else
        echo -e "${GREEN}✅ Роутер уже подключен независимо${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Роутер не подключен, добавляем...${NC}"
    
    # Добавляем импорт если его нет
    if ! grep -q "from security.api.routers.metrics_router import" "$MAIN_PY"; then
        echo "   Добавляем импорт..."
        # Находим место после других импортов роутеров
        sed -i '/from security.api.routers.*router import/a try:\n    from security.api.routers.metrics_router import router as metrics_router\n    metrics_router_available = True\nexcept ImportError as e:\n    print(f"⚠️ metrics_router недоступен: {e}")\n    metrics_router_available = False\n    metrics_router = None' "$MAIN_PY"
    fi
    
    # Добавляем подключение роутера
    python3 << 'PYTHON_SCRIPT'
main_py_path = "/opt/aladdin-backend/main.py"

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем место после других роутеров
if "app.include_router" in content:
    # Добавляем после последнего include_router
    pattern = r'(app\.include_router\([^)]+\)\s*\n)'
    replacement = r'\1\nif metrics_router_available:\n    try:\n        app.include_router(metrics_router)\n        print("✅ Роутер Metrics подключен")\n    except Exception as e:\n        print(f"❌ Ошибка подключения Metrics: {e}")\n'
    content = re.sub(pattern, replacement, content)
else:
    # Добавляем в конец перед запуском
    content += '\nif metrics_router_available:\n    try:\n        app.include_router(metrics_router)\n        print("✅ Роутер Metrics подключен")\n    except Exception as e:\n        print(f"❌ Ошибка подключения Metrics: {e}")\n'

with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Роутер добавлен")
PYTHON_SCRIPT
fi

# 3. Проверка синтаксиса Python
echo ""
echo "3️⃣ Проверка синтаксиса Python..."
if python3 -m py_compile "$MAIN_PY" 2>/dev/null; then
    echo -e "${GREEN}✅ Синтаксис правильный${NC}"
else
    echo -e "${RED}❌ Ошибка синтаксиса!${NC}"
    echo "   Восстанавливаем резервную копию..."
    cp "$BACKUP_FILE" "$MAIN_PY"
    exit 1
fi

# 4. Перезапуск сервиса
echo ""
echo "4️⃣ Перезапуск сервиса..."
systemctl restart aladdin-production-api
sleep 5

if systemctl is-active --quiet aladdin-production-api; then
    echo -e "${GREEN}✅ Сервис перезапущен успешно${NC}"
else
    echo -e "${RED}❌ Ошибка перезапуска сервиса!${NC}"
    echo "   Восстанавливаем резервную копию..."
    cp "$BACKUP_FILE" "$MAIN_PY"
    systemctl restart aladdin-production-api
    exit 1
fi

# 5. Проверка логов
echo ""
echo "5️⃣ Проверка логов (последние 10 строк)..."
journalctl -u aladdin-production-api -n 20 --no-pager | tail -10

# 6. Тестирование endpoint
echo ""
echo "6️⃣ Тестирование endpoint..."
sleep 2
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test_fix","appVersion":"1.0.0","platform":"ios","metrics":[]}')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Endpoint работает! HTTP $HTTP_CODE${NC}"
    echo "   Ответ: $BODY"
    echo ""
    echo -e "${GREEN}=== ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО! ===${NC}"
else
    echo -e "${RED}❌ Endpoint все еще возвращает HTTP $HTTP_CODE${NC}"
    echo "   Ответ: $BODY"
    echo ""
    echo "   Проверьте логи сервера для деталей"
fi
