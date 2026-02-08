#!/bin/bash

# 🚀 CRASH DETECTION - КОРРЕКТНЫЙ СКРИПТ ТЕСТИРОВАНИЯ
# Дата: 6 февраля 2026 г.
# Цель: Получить ВЕРНЫЕ данные производительности

echo "🧪 CRASH DETECTION - КОРРЕКТНОЕ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ"
echo "==============================================================="
echo ""

# Настройки
SERVER="http://149.154.65.180:8002"
LOG_FILE="crash_detection_test_$(date +%Y%m%d_%H%M%S).log"
ITERATIONS=10

echo "📋 КОНФИГУРАЦИЯ ТЕСТИРОВАНИЯ:"
echo "  Сервер: $SERVER"
echo "  Итераций на эндпоинт: $ITERATIONS"
echo "  Лог файл: $LOG_FILE"
echo "  Дата: $(date)"
echo ""

# Функция для получения тестовых данных для POST запросов
get_test_data() {
    case $1 in
        "/api/crash-detection/setup")
            echo '{"latitude":55.7558,"longitude":37.6173,"radius":500}'
            ;;
        "/api/crash-detection/start"|"/api/crash-detection/stop")
            echo '{}'
            ;;
        "/api/crash-detection/data")
            echo '{"accelerometer":{"x":0,"y":0,"z":9.8},"gyroscope":{"x":0,"y":0,"z":0},"speed":0,"latitude":55.7558,"longitude":37.6173,"timestamp":'$(date +%s)'000}'
            ;;
        "/api/crash-detection/alert")
            echo '{"latitude":55.7558,"longitude":37.6173,"severity":"high"}'
            ;;
        *)
            echo '{}'
            ;;
    esac
}

# Функция для выполнения одного теста
run_test() {
    local method=$1
    local endpoint=$2
    local iteration=$3

    local url="$SERVER$endpoint"
    local test_data=$(get_test_data $endpoint)
    local timestamp=$(date +%s%N)

    echo -n "  [$iteration] $method $endpoint ... "

    # Выполнение запроса
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "@curl-format.txt" -X GET "$url" 2>/dev/null)
    else
        response=$(curl -s -w "@curl-format.txt" -X POST "$url" \
                  -H "Content-Type: application/json" \
                  -d "$test_data" 2>/dev/null)
    fi

    # Парсинг ответа
    local http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d' ' -f2)
    local total_time=$(echo "$response" | grep "TOTAL_TIME" | cut -d' ' -f2)
    local response_body=$(echo "$response" | sed '/^HTTP_CODE\|^TOTAL_TIME\|^REDIRECT_COUNT\|^SIZE/d')

    # Проверка SFM интеграции
    local sfm_status="NO_SFM"
    if echo "$response_body" | grep -q '"source":"real_sfm"'; then
        sfm_status="SFM_OK"
    fi

    # Вычисление времени в ms
    local time_ms=$(echo "$total_time * 1000" | bc 2>/dev/null || echo "0")
    local time_formatted=$(printf "%.2f" $time_ms 2>/dev/null || echo "0.00")

    # Статус теста
    local status="UNKNOWN"
    if [ "$http_code" = "200" ] && [ "$sfm_status" = "SFM_OK" ]; then
        status="✅ OK"
    elif [ "$http_code" = "200" ]; then
        status="⚠️ NO_SFM"
    else
        status="❌ ERROR_$http_code"
    fi

    echo "$status | ${time_formatted}ms | SFM: $sfm_status"

    # Логирование
    echo "$timestamp|$method|$endpoint|$iteration|$http_code|$time_ms|$sfm_status|$response_body" >> "$LOG_FILE"

    # Возврат времени для статистики
    echo "$time_ms"
}

# Создание файла формата для curl
cat > curl-format.txt << 'EOF'
HTTP_CODE: %{http_code}
TOTAL_TIME: %{time_total}
REDIRECT_COUNT: %{redirect_url}
SIZE: %{size_download}
%{stderr}
EOF

# Основные эндпоинты для тестирования
ENDPOINTS=(
    "GET /api/health"
    "GET /api/crash-detection/status"
    "POST /api/crash-detection/setup"
    "POST /api/crash-detection/start"
    "POST /api/crash-detection/data"
    "POST /api/crash-detection/alert"
    "POST /api/crash-detection/stop"
)

# Основной цикл тестирования
echo "🧪 НАЧИНАЮ ТЕСТИРОВАНИЕ..."
echo ""

all_times=()
endpoint_stats=()

for endpoint_config in "${ENDPOINTS[@]}"; do
    method=$(echo $endpoint_config | cut -d' ' -f1)
    endpoint=$(echo $endpoint_config | cut -d' ' -f2)

    echo "🎯 ТЕСТИРОВАНИЕ: $method $endpoint"
    echo "  Выполняю $ITERATIONS итераций..."
    echo ""

    endpoint_times=()

    for i in $(seq 1 $ITERATIONS); do
        time_ms=$(run_test "$method" "$endpoint" "$i")
        endpoint_times+=("$time_ms")
        all_times+=("$time_ms")

        # Небольшая задержка между запросами
        sleep 0.1
    done

    echo ""

    # Статистика по эндпоинту
    if [ ${#endpoint_times[@]} -gt 0 ]; then
        # Расчет статистики
        sum=0
        min=999999
        max=0
        for t in "${endpoint_times[@]}"; do
            sum=$(echo "$sum + $t" | bc 2>/dev/null || echo "$sum")
            [ "$(echo "$t < $min" | bc 2>/dev/null)" = "1" ] && min=$t
            [ "$(echo "$t > $max" | bc 2>/dev/null)" = "1" ] && max=$t
        done

        avg=$(echo "scale=2; $sum / ${#endpoint_times[@]}" | bc 2>/dev/null || echo "0")
        p95=$(echo "${endpoint_times[@]}" | tr ' ' '\n' | sort -n | sed -n '19p' 2>/dev/null || echo "$max")

        echo "  📊 СТАТИСТИКА $endpoint:"
        echo "    Среднее: ${avg}ms"
        echo "    Минимум: ${min}ms"
        echo "    Максимум: ${max}ms"
        echo "    P95: ${p95}ms"
        echo ""

        endpoint_stats+=("$endpoint|$avg|$min|$max|$p95")
    fi
done

# Финальная статистика
echo "🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!"
echo "=========================="
echo ""

if [ ${#all_times[@]} -gt 0 ]; then
    echo "📈 ОБЩАЯ СТАТИСТИКА ПО ВСЕМ ЭНДПОИНТАМ:"
    echo ""

    # Общая статистика
    total_sum=0
    total_min=999999
    total_max=0

    for t in "${all_times[@]}"; do
        total_sum=$(echo "$total_sum + $t" | bc 2>/dev/null || echo "$total_sum")
        [ "$(echo "$t < $total_min" | bc 2>/dev/null)" = "1" ] && total_min=$t
        [ "$(echo "$t > $total_max" | bc 2>/dev/null)" = "1" ] && total_max=$t
    done

    total_avg=$(echo "scale=2; $total_sum / ${#all_times[@]}" | bc 2>/dev/null || echo "0")
    total_p95=$(echo "${all_times[@]}" | tr ' ' '\n' | sort -n | sed -n '57p' 2>/dev/null || echo "$total_max")

    echo "  • Общее среднее время: ${total_avg}ms"
    echo "  • Минимальное время: ${total_min}ms"
    echo "  • Максимальное время: ${total_max}ms"
    echo "  • 95-й перцентиль: ${total_p95}ms"
    echo "  • Всего запросов: ${#all_times[@]}"
    echo ""

    # Сравнение с целями
    echo "🎯 СРАВНЕНИЕ С ЦЕЛЯМИ:"
    if (( $(echo "$total_avg < 15" | bc -l 2>/dev/null || echo "0") )); then
        echo "  ✅ Среднее время: ${total_avg}ms < 15ms (ЦЕЛЬ ДОСТИГНУТА!)"
    else
        deviation=$(echo "scale=1; $total_avg / 15" | bc 2>/dev/null || echo "0")
        echo "  ❌ Среднее время: ${total_avg}ms > 15ms (Отклонение: ${deviation}x)"
    fi

    if (( $(echo "$total_p95 < 25" | bc -l 2>/dev/null || echo "0") )); then
        echo "  ✅ P95 перцентиль: ${total_p95}ms < 25ms (ЦЕЛЬ ДОСТИГНУТА!)"
    else
        echo "  ❌ P95 перцентиль: ${total_p95}ms > 25ms"
    fi
    echo ""

    # Статистика по эндпоинтам
    echo "📋 ПОДРОБНАЯ СТАТИСТИКА ПО ЭНДПОИНТАМ:"
    echo "  Эндпоинт                    | Среднее | Мин | Макс | P95"
    echo "  -----------------------------|---------|-----|-----|-----"
    for stat in "${endpoint_stats[@]}"; do
        IFS='|' read -r ep avg min max p95 <<< "$stat"
        printf "  %-28s | %7sms | %3sms | %3sms | %3sms\n" "$ep" "$avg" "$min" "$max" "$p95"
    done
else
    echo "❌ НЕТ ДАННЫХ ДЛЯ АНАЛИЗА"
fi

echo ""
echo "📝 ЛОГИ СОХРАНЕНЫ В: $LOG_FILE"
echo "🕒 ВРЕМЯ ТЕСТИРОВАНИЯ: $(date)"
echo ""

# Очистка временных файлов
rm -f curl-format.txt

echo "✅ КОРРЕКТНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!"
echo "====================================="