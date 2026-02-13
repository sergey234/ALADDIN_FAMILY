#!/bin/bash

# 🚀 ПОЛНЫЙ СКРИПТ ДЛЯ ВЫПОЛНЕНИЯ НА СЕРВЕРЕ
# Дата: 2026-02-13
# Цель: Проверить и исправить все проблемы для продакшн

set -e  # Остановка при ошибке

echo "============================================================"
echo "🚀 ПОЛНАЯ ПРОВЕРКА И ИСПРАВЛЕНИЕ ДЛЯ ПРОДАКШН"
echo "============================================================"
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /opt/aladdin-backend

# ============================================================
# 1. ПРОВЕРКА METRICS ROUTER
# ============================================================

echo -e "${BLUE}1️⃣ ПРОВЕРКА METRICS ROUTER${NC}"
echo ""

# 1.1 Проверка файла
echo "   Проверка файла metrics_router.py..."
if [ -f "security/api/routers/metrics_router.py" ]; then
    echo -e "   ${GREEN}✅ Файл существует${NC}"
    SIZE=$(ls -lh security/api/routers/metrics_router.py | awk '{print $5}')
    echo "   Размер: $SIZE"
else
    echo -e "   ${RED}❌ Файл НЕ найден!${NC}"
    exit 1
fi

# 1.2 Проверка префикса
echo ""
echo "   Проверка префикса роутера..."
PREFIX=$(grep -oP 'prefix=["\047]?[^"\047]*["\047]?' security/api/routers/metrics_router.py | head -1 | grep -oP '["\047]?[^"\047]+["\047]?' | tr -d '"'"'')
echo "   Найден префикс: $PREFIX"
if [ "$PREFIX" = "/metrics" ]; then
    echo -e "   ${GREEN}✅ Префикс правильный${NC}"
elif [ "$PREFIX" = "/api/metrics" ]; then
    echo -e "   ${YELLOW}⚠️ Префикс неправильный - исправляем...${NC}"
    sed -i 's|prefix="/api/metrics"|prefix="/metrics"|g' security/api/routers/metrics_router.py
    sed -i "s|prefix='/api/metrics'|prefix='/metrics'|g" security/api/routers/metrics_router.py
    echo -e "   ${GREEN}✅ Префикс исправлен${NC}"
else
    echo -e "   ${YELLOW}⚠️ Неожиданный префикс: $PREFIX${NC}"
fi

# 1.3 Проверка подключения в main.py
echo ""
echo "   Проверка подключения в main.py..."
if grep -q "metrics_router" main.py; then
    echo -e "   ${GREEN}✅ metrics_router найден в main.py${NC}"
    
    # Проверяем независимость
    if grep -A 5 "if metrics_router_available:" main.py | grep -q "if system_router_available:" || \
       grep -B 5 "if metrics_router_available:" main.py | grep -q "if system_router_available:"; then
        echo -e "   ${YELLOW}⚠️ Роутер подключен условно - исправляем...${NC}"
        
        # Создаем резервную копию
        BACKUP="main.py.backup_$(date +%Y%m%d_%H%M%S)"
        cp main.py "$BACKUP"
        echo "   Резервная копия: $BACKUP"
        
        # Исправляем через Python (более надежно)
        python3 << 'PYTHON_FIX'
import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем блок с metrics_router внутри system_router
pattern = r'(if system_router_available:.*?app\.include_router\(system_router\).*?\n)(\s+if metrics_router_available:.*?app\.include_router\(metrics_router\).*?\n)'

def fix_metrics(match):
    system_block = match.group(1)
    # Убираем metrics из system блока и делаем независимым
    new_content = system_block
    new_content += "\n# Независимо от system_router\nif metrics_router_available:\n    try:\n        app.include_router(metrics_router)\n        print(\"✅ Роутер Metrics подключен\")\n    except Exception as e:\n        print(f\"❌ Ошибка подключения Metrics: {e}\")\n"
    return new_content

new_content = re.sub(pattern, fix_metrics, content, flags=re.DOTALL)

# Если не нашлось, проверяем другой паттерн
if new_content == content:
    # Ищем просто наличие внутри блока
    lines = content.split('\n')
    new_lines = []
    in_system_block = False
    metrics_found = False
    
    for i, line in enumerate(lines):
        if 'if system_router_available:' in line:
            in_system_block = True
            new_lines.append(line)
        elif in_system_block and 'if metrics_router_available:' in line:
            metrics_found = True
            # Пропускаем эту строку и следующие до конца блока metrics
            continue
        elif in_system_block and metrics_found and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # Конец system блока
            in_system_block = False
            metrics_found = False
            # Добавляем независимый блок metrics
            new_lines.append("")
            new_lines.append("# Независимо от system_router")
            new_lines.append("if metrics_router_available:")
            new_lines.append("    try:")
            new_lines.append("        app.include_router(metrics_router)")
            new_lines.append("        print(\"✅ Роутер Metrics подключен\")")
            new_lines.append("    except Exception as e:")
            new_lines.append("        print(f\"❌ Ошибка подключения Metrics: {e}\")")
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    if metrics_found:
        new_content = '\n'.join(new_lines)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Исправлено")
PYTHON_FIX
        
        echo -e "   ${GREEN}✅ Роутер сделан независимым${NC}"
    else
        echo -e "   ${GREEN}✅ Роутер уже подключен независимо${NC}"
    fi
else
    echo -e "   ${RED}❌ metrics_router НЕ найден в main.py!${NC}"
    echo "   Нужно добавить вручную (см. SSH_COMMANDS_FOR_SERVER.md)"
    exit 1
fi

# ============================================================
# 2. ПЕРЕЗАПУСК СЕРВИСА
# ============================================================

echo ""
echo -e "${BLUE}2️⃣ ПЕРЕЗАПУСК СЕРВИСА${NC}"
echo ""

echo "   Остановка сервиса..."
sudo systemctl stop aladdin-production-api
sleep 2

echo "   Запуск сервиса..."
sudo systemctl start aladdin-production-api
sleep 5

echo "   Проверка статуса..."
if systemctl is-active --quiet aladdin-production-api; then
    echo -e "   ${GREEN}✅ Сервис активен${NC}"
else
    echo -e "   ${RED}❌ Сервис НЕ активен!${NC}"
    echo "   Проверьте логи: journalctl -u aladdin-production-api -n 50"
    exit 1
fi

# ============================================================
# 3. ПРОВЕРКА ЛОГОВ
# ============================================================

echo ""
echo -e "${BLUE}3️⃣ ПРОВЕРКА ЛОГОВ${NC}"
echo ""

echo "   Последние записи о metrics:"
journalctl -u aladdin-production-api -n 50 --no-pager | grep -i metrics | tail -5 || echo "   Нет записей о metrics"

echo ""
echo "   Общий статус сервиса:"
systemctl status aladdin-production-api --no-pager -l | head -15

# ============================================================
# 4. ТЕСТИРОВАНИЕ ENDPOINT
# ============================================================

echo ""
echo -e "${BLUE}4️⃣ ТЕСТИРОВАНИЕ ENDPOINT${NC}"
echo ""

echo "   Отправка тестового запроса..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"server_test","appVersion":"1.0.0","platform":"ios","metrics":[{"type":"user_action","timestamp":1234567890.0,"action":"test"}]}' \
  --max-time 10)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "   ${GREEN}✅ Endpoint работает! HTTP $HTTP_CODE${NC}"
    echo "   Ответ: $BODY"
    echo ""
    echo -e "${GREEN}============================================================"
    echo "✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!"
    echo "============================================================${NC}"
    exit 0
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "   ${RED}❌ Endpoint все еще возвращает 404!${NC}"
    echo "   Ответ: $BODY"
    echo ""
    echo "   Проверьте:"
    echo "   1. Логи сервера: journalctl -u aladdin-production-api -n 100"
    echo "   2. Подключение роутера в main.py"
    echo "   3. Префикс роутера"
    exit 1
else
    echo -e "   ${YELLOW}⚠️ Endpoint возвращает HTTP $HTTP_CODE${NC}"
    echo "   Ответ: $BODY"
    echo ""
    echo "   Проверьте логи для деталей"
    exit 1
fi
