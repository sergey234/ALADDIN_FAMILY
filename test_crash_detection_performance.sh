#!/bin/bash

# 🧪 CRASH DETECTION - КОРРЕКТНОЕ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ
# Дата: 6 февраля 2026 г.
# Цель: Получить ВЕРНЫЕ данные производительности

SERVER="149.154.65.180:8002"
BASE_URL="http://${SERVER}"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ ЭНДПОИНТОВ CRASH DETECTION"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Функция для тестирования эндпоинта
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local name=$4
    
    echo "$name $method $endpoint"
    
    times=()
    errors=0
    sfm_count=0
    
    for i in {1..10}; do
        if [ "$method" = "GET" ]; then
            result=$(curl -s -w "%{time_total}|%{http_code}" -o /tmp/response.json "$BASE_URL$endpoint" 2>/dev/null)
        else
            result=$(curl -s -w "%{time_total}|%{http_code}" -o /tmp/response.json -X POST \
                -H "Content-Type: application/json" \
                -d "$data" \
                "$BASE_URL$endpoint" 2>/dev/null)
        fi
        
        time_total=$(echo "$result" | cut -d'|' -f1)
        http_code=$(echo "$result" | cut -d'|' -f2)
        
        if [ "$http_code" = "200" ]; then
            time_ms=$(echo "$time_total * 1000" | bc 2>/dev/null || echo "0")
            times+=("$time_ms")
            
            if grep -q '"source":"real_sfm"' /tmp/response.json 2>/dev/null; then
                sfm_count=$((sfm_count + 1))
            fi
        else
            errors=$((errors + 1))
        fi
        
        sleep 0.1
    done
    
    if [ ${#times[@]} -gt 0 ]; then
        # Расчет статистики
        sum=0
        min=999999
        max=0
        for t in "${times[@]}"; do
            sum=$(echo "$sum + $t" | bc 2>/dev/null || echo "$sum")
            if (( $(echo "$t < $min" | bc -l 2>/dev/null || echo "0") )); then
                min=$t
            fi
            if (( $(echo "$t > $max" | bc -l 2>/dev/null || echo "0") )); then
                max=$t
            fi
        done
        
        avg=$(echo "scale=2; $sum / ${#times[@]}" | bc 2>/dev/null || echo "0")
        sorted_times=($(printf '%s\n' "${times[@]}" | sort -n))
        p95_idx=$(( ${#times[@]} * 95 / 100 ))
        p95=${sorted_times[$p95_idx]}
        
        status="✅"
        if (( $(echo "$avg > 15" | bc -l 2>/dev/null || echo "1") )); then
            status="❌"
        fi
        
        echo "  $status Среднее: ${avg}ms | Min: ${min}ms | Max: ${max}ms | P95: ${p95}ms | Ошибок: $errors | SFM: $sfm_count/10"
        echo ""
        
        # Сохранение результатов
        echo "${endpoint}|${avg}|${min}|${max}|${p95}|${errors}|${sfm_count}" >> /tmp/crash_test_results.txt
    else
        echo "  ❌ Нет успешных запросов"
        echo ""
    fi
}

# Очистка предыдущих результатов
rm -f /tmp/crash_test_results.txt
rm -f /tmp/response.json

# Тестирование всех эндпоинтов
test_endpoint "GET" "/api/health" "" "1️⃣ Health"
test_endpoint "GET" "/api/crash-detection/status" "" "2️⃣ Status"
test_endpoint "POST" "/api/crash-detection/setup" '{"latitude":55.7558,"longitude":37.6173,"radius":500}' "3️⃣ Setup"
test_endpoint "POST" "/api/crash-detection/start" '{}' "4️⃣ Start"
test_endpoint "POST" "/api/crash-detection/data" '{"accelerometer":{"x":0,"y":0,"z":9.8},"gyroscope":{"x":0,"y":0,"z":0},"speed":0,"timestamp":'$(date +%s)'000}' "5️⃣ Data"
test_endpoint "POST" "/api/crash-detection/alert" '{"latitude":55.7558,"longitude":37.6173,"severity":"high"}' "6️⃣ Alert"
test_endpoint "POST" "/api/crash-detection/stop" '{}' "7️⃣ Stop"

# Итоговая статистика
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 ИТОГОВАЯ СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ:"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f /tmp/crash_test_results.txt ]; then
    total_avg=0
    total_min=999999
    total_max=0
    total_errors=0
    total_sfm=0
    count=0
    
    while IFS='|' read -r ep avg min max p95 errors sfm; do
        total_avg=$(echo "$total_avg + $avg" | bc 2>/dev/null || echo "$total_avg")
        if (( $(echo "$min < $total_min" | bc -l 2>/dev/null || echo "0") )); then
            total_min=$min
        fi
        if (( $(echo "$max > $total_max" | bc -l 2>/dev/null || echo "0") )); then
            total_max=$max
        fi
        total_errors=$((total_errors + errors))
        total_sfm=$((total_sfm + sfm))
        count=$((count + 1))
    done < /tmp/crash_test_results.txt
    
    if [ $count -gt 0 ]; then
        overall_avg=$(echo "scale=2; $total_avg / $count" | bc 2>/dev/null || echo "0")
        
        echo "Среднее время всех эндпоинтов: ${overall_avg}ms"
        echo "Минимум: ${total_min}ms"
        echo "Максимум: ${total_max}ms"
        echo "Всего ошибок: ${total_errors}/70"
        echo "SFM интеграция: ${total_sfm}/70 ($((total_sfm * 100 / 70))%)"
        echo ""
        echo "Цель: <15ms среднее, <25ms P95"
        
        if (( $(echo "$overall_avg < 15" | bc -l 2>/dev/null || echo "0") )); then
            echo "Статус: ✅ ОПТИМИЗИРОВАНО"
        else
            deviation=$(echo "scale=1; $overall_avg / 15" | bc 2>/dev/null || echo "0")
            echo "Статус: ❌ ТРЕБУЕТ ОПТИМИЗАЦИИ (в ${deviation}x раз выше цели)"
        fi
    fi
fi

echo ""
echo "✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!"
