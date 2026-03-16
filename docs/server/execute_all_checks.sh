#!/bin/bash
# Скрипт для выполнения всех проверок на сервере
# ЭТАП 5.2, 6.1-6.4

set -e

echo "=========================================="
echo "ВЫПОЛНЕНИЕ ВСЕХ ПРОВЕРОК НА СЕРВЕРЕ"
echo "=========================================="
echo ""

cd /opt/aladdin-backend

# Создать директорию для скриптов
mkdir -p docs/server

# ЭТАП 5.2: Проверка SFM.execute_function
echo "=========================================="
echo "ЭТАП 5.2: Проверка SFM.execute_function"
echo "=========================================="
if [ -f "docs/server/test_sfm_execute_function.py" ]; then
    python3 docs/server/test_sfm_execute_function.py
    echo "✅ ЭТАП 5.2 завершен"
else
    echo "⚠️ Скрипт test_sfm_execute_function.py не найден"
fi
echo ""

# ЭТАП 6.1-6.3: Проверка API endpoints
echo "=========================================="
echo "ЭТАП 6.1-6.3: Проверка API endpoints"
echo "=========================================="
if [ -f "docs/server/test_security_functions_api.py" ]; then
    # Попробовать получить токен из переменной окружения или создать тестовый
    if [ -z "$AUTH_TOKEN" ]; then
        echo "⚠️ AUTH_TOKEN не установлен, пропускаем проверку API"
        echo "   Установите токен: export AUTH_TOKEN='your_token'"
    else
        python3 docs/server/test_security_functions_api.py
        echo "✅ ЭТАП 6.1-6.3 завершен"
    fi
else
    echo "⚠️ Скрипт test_security_functions_api.py не найден"
fi
echo ""

# ЭТАП 6.4: Проверка соответствия тарифам
echo "=========================================="
echo "ЭТАП 6.4: Проверка соответствия тарифам"
echo "=========================================="
python3 << 'EOF'
import psycopg2
import sys

try:
    # Подключиться к БД
    conn = psycopg2.connect(
        host="localhost",
        database="aladdin_db",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    
    # Проверить функции по тарифам
    query = """
    SELECT 
        tariff_type,
        COUNT(DISTINCT component_id) as functions_count
    FROM component_status
    WHERE is_enabled = true
    GROUP BY tariff_type
    ORDER BY tariff_type;
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    print("Результаты проверки тарифов:")
    print("-" * 50)
    
    expected = {
        "FREE": 26,
        "PERSONAL": 69,
        "FAMILY": 124,
        "PREMIUM": 138
    }
    
    all_correct = True
    for tariff_type, count in results:
        expected_count = expected.get(tariff_type, 0)
        status = "✅" if count == expected_count else "❌"
        print(f"{status} {tariff_type}: {count} (ожидается: {expected_count})")
        if count != expected_count:
            all_correct = False
    
    if all_correct:
        print("\n✅ Все тарифы соответствуют ожидаемым значениям!")
    else:
        print("\n⚠️ Некоторые тарифы не соответствуют ожидаемым значениям")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка при проверке тарифов: {e}")
    sys.exit(1)
EOF

echo "✅ ЭТАП 6.4 завершен"
echo ""

echo "=========================================="
echo "ВСЕ ПРОВЕРКИ ЗАВЕРШЕНЫ"
echo "=========================================="
