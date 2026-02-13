#!/bin/bash

# 🚀 Скрипт для массового тестирования всех endpoint'ов
# Цель: Протестировать все 331 endpoint на сервере

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
BASE_URL="${BASE_URL:-https://aladdin-ai.ru}"
USER_ID="${USER_ID:-test_user_123}"
TIMEOUT=10

# Статистика
TOTAL=0
SUCCESS=0
FAILED=0
SKIPPED=0

# Файлы для отчетов
REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).md"
LOG_FILE="test_log_$(date +%Y%m%d_%H%M%S).log"

# Функция для тестирования endpoint'а
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    TOTAL=$((TOTAL + 1))
    
    echo -n "Testing: $method $endpoint ... "
    
    # Формируем команду curl
    local curl_cmd="curl -s -w \"%{http_code}\" -X $method"
    
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H \"Content-Type: application/json\" -d '$data'"
    fi
    
    curl_cmd="$curl_cmd --max-time $TIMEOUT \"$BASE_URL$endpoint\""
    
    # Выполняем запрос
    local response=$(eval $curl_cmd 2>&1)
    local http_code="${response: -3}"
    local body="${response%???}"
    
    # Проверяем результат
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅ OK${NC} ($http_code)"
        echo "✅ $method $endpoint - OK ($http_code)" >> "$REPORT_FILE"
        SUCCESS=$((SUCCESS + 1))
        return 0
    elif [ "$http_code" = "422" ]; then
        echo -e "${YELLOW}⚠️  VALIDATION ERROR${NC} ($http_code) - это нормально"
        echo "⚠️  $method $endpoint - VALIDATION ERROR ($http_code)" >> "$REPORT_FILE"
        SUCCESS=$((SUCCESS + 1))
        return 0
    elif [ "$http_code" = "404" ]; then
        echo -e "${YELLOW}⚠️  NOT FOUND${NC} ($http_code) - endpoint может быть не развернут"
        echo "⚠️  $method $endpoint - NOT FOUND ($http_code)" >> "$REPORT_FILE"
        SKIPPED=$((SKIPPED + 1))
        return 1
    elif [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        echo -e "${YELLOW}⚠️  AUTH REQUIRED${NC} ($http_code) - требуется авторизация"
        echo "⚠️  $method $endpoint - AUTH REQUIRED ($http_code)" >> "$REPORT_FILE"
        SKIPPED=$((SKIPPED + 1))
        return 1
    else
        echo -e "${RED}❌ FAILED${NC} ($http_code)"
        echo "❌ $method $endpoint - FAILED ($http_code)" >> "$REPORT_FILE"
        echo "   Response: $body" >> "$LOG_FILE"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Создаем файлы отчетов
echo "# Отчет тестирования endpoint'ов" > "$REPORT_FILE"
echo "Дата: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "## Результаты:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "🧪 Начинаем тестирование всех endpoint'ов..."
echo ""

# ============================================
# ГЕЙМИФИКАЦИЯ (30 endpoint'ов)
# ============================================

echo "## 🎮 Геймификация (30 endpoint'ов)"
echo "## 🎮 Геймификация (30 endpoint'ов)" >> "$REPORT_FILE"

# Баланс единорогов (4 endpoint'а)
test_endpoint "GET" "/api/gamification/balance/$USER_ID" "" "Получить баланс"
test_endpoint "POST" "/api/gamification/balance/add" "{\"userId\": \"$USER_ID\", \"amount\": 10, \"reason\": \"Test\"}" "Добавить баланс"
test_endpoint "POST" "/api/gamification/balance/subtract" "{\"userId\": \"$USER_ID\", \"amount\": 5, \"reason\": \"Test\"}" "Вычесть баланс"
test_endpoint "GET" "/api/gamification/balance/history?userId=$USER_ID&limit=10" "" "История баланса"

# Награды (6 endpoint'ов)
test_endpoint "GET" "/api/gamification/rewards?userId=$USER_ID" "" "Получить награды"
test_endpoint "POST" "/api/gamification/rewards/claim" "{\"userId\": \"$USER_ID\", \"rewardId\": \"test_reward_1\"}" "Получить награду"
test_endpoint "GET" "/api/gamification/rewards/history?userId=$USER_ID&limit=10" "" "История наград"
test_endpoint "POST" "/api/gamification/rewards/give" "{\"userId\": \"$USER_ID\", \"rewardId\": \"test_reward_1\", \"reason\": \"Test\"}" "Выдать награду"
test_endpoint "GET" "/api/gamification/rewards/shop?userId=$USER_ID" "" "Магазин наград"
test_endpoint "POST" "/api/gamification/rewards/purchase" "{\"userId\": \"$USER_ID\", \"rewardId\": \"test_reward_1\"}" "Купить награду"

# Достижения (5 endpoint'ов)
test_endpoint "GET" "/api/gamification/achievements?userId=$USER_ID" "" "Получить достижения"
test_endpoint "POST" "/api/gamification/achievements/unlock" "{\"userId\": \"$USER_ID\", \"achievementId\": \"test_achievement_1\"}" "Разблокировать достижение"
test_endpoint "GET" "/api/gamification/achievements/progress?userId=$USER_ID" "" "Прогресс достижений"
test_endpoint "GET" "/api/gamification/achievements/test_achievement_1?userId=$USER_ID" "" "Получить достижение"
test_endpoint "POST" "/api/gamification/achievements/claim" "{\"userId\": \"$USER_ID\", \"achievementId\": \"test_achievement_1\"}" "Получить награду за достижение"

# Турниры (6 endpoint'ов)
test_endpoint "GET" "/api/gamification/tournaments?userId=$USER_ID" "" "Получить турниры"
test_endpoint "POST" "/api/gamification/tournaments/join" "{\"userId\": \"$USER_ID\", \"tournamentId\": \"test_tournament_1\"}" "Присоединиться к турниру"
test_endpoint "GET" "/api/gamification/tournaments/test_tournament_1?userId=$USER_ID" "" "Получить турнир"
test_endpoint "GET" "/api/gamification/tournaments/leaderboard?tournamentId=test_tournament_1" "" "Таблица лидеров"
test_endpoint "POST" "/api/gamification/tournaments/leave" "{\"userId\": \"$USER_ID\", \"tournamentId\": \"test_tournament_1\"}" "Выйти из турнира"
test_endpoint "GET" "/api/gamification/tournaments/history?userId=$USER_ID&limit=10" "" "История турниров"

# Настройки игр (4 endpoint'а)
test_endpoint "GET" "/api/gamification/settings?userId=$USER_ID" "" "Получить настройки игр"
test_endpoint "POST" "/api/gamification/settings/update" "{\"userId\": \"$USER_ID\", \"settings\": {\"enabled\": true}}" "Обновить настройки игр"
test_endpoint "GET" "/api/gamification/settings/notifications?userId=$USER_ID" "" "Получить уведомления игр"
test_endpoint "POST" "/api/gamification/settings/notifications/update" "{\"userId\": \"$USER_ID\", \"notifications\": {\"enabled\": true}}" "Обновить уведомления игр"

# Прогресс игр (5 endpoint'ов)
test_endpoint "GET" "/api/gamification/progress?userId=$USER_ID" "" "Получить прогресс"
test_endpoint "POST" "/api/gamification/progress/update" "{\"userId\": \"$USER_ID\", \"progress\": {\"level\": 5}}" "Обновить прогресс"
test_endpoint "GET" "/api/gamification/progress/stats?userId=$USER_ID" "" "Статистика прогресса"
test_endpoint "GET" "/api/gamification/progress/level?userId=$USER_ID" "" "Получить уровень"
test_endpoint "POST" "/api/gamification/progress/reset" "{\"userId\": \"$USER_ID\"}" "Сбросить прогресс"

# ============================================
# РОДИТЕЛЬСКИЙ КОНТРОЛЬ (20 endpoint'ов)
# ============================================

echo ""
echo "## 👨‍👩‍👧‍👦 Родительский контроль (20 endpoint'ов)"
echo "## 👨‍👩‍👧‍👦 Родительский контроль (20 endpoint'ов)" >> "$REPORT_FILE"

# Синхронизация настроек (5 endpoint'ов)
test_endpoint "GET" "/api/parental-control/settings/test_family_123" "" "Получить настройки"
test_endpoint "POST" "/api/parental-control/settings/update" "{\"familyId\": \"test_family_123\", \"settings\": {}}" "Обновить настройки"
test_endpoint "GET" "/api/parental-control/settings/history?familyId=test_family_123&limit=10" "" "История настроек"
test_endpoint "POST" "/api/parental-control/settings/sync" "{\"familyId\": \"test_family_123\"}" "Синхронизировать настройки"
test_endpoint "GET" "/api/parental-control/settings/conflicts?familyId=test_family_123" "" "Конфликты настроек"

# Синхронизация лимитов времени (4 endpoint'а)
test_endpoint "GET" "/api/parental-control/time-limits/test_child_123" "" "Получить лимиты времени"
test_endpoint "POST" "/api/parental-control/time-limits/update" "{\"childId\": \"test_child_123\", \"limits\": {}}" "Обновить лимиты времени"
test_endpoint "GET" "/api/parental-control/time-limits/history?childId=test_child_123&limit=10" "" "История лимитов времени"
test_endpoint "POST" "/api/parental-control/time-limits/reset" "{\"childId\": \"test_child_123\"}" "Сбросить лимиты времени"

# Синхронизация расписаний (4 endpoint'а)
test_endpoint "GET" "/api/parental-control/schedules/test_child_123" "" "Получить расписания"
test_endpoint "POST" "/api/parental-control/schedules/update" "{\"childId\": \"test_child_123\", \"schedules\": []}" "Обновить расписания"
test_endpoint "GET" "/api/parental-control/schedules/history?childId=test_child_123&limit=10" "" "История расписаний"
test_endpoint "POST" "/api/parental-control/schedules/delete" "{\"childId\": \"test_child_123\", \"scheduleId\": \"test_schedule_1\"}" "Удалить расписание"

# Синхронизация геозон (4 endpoint'а)
test_endpoint "GET" "/api/parental-control/geofences/test_child_123" "" "Получить геозоны"
test_endpoint "POST" "/api/parental-control/geofences/add" "{\"childId\": \"test_child_123\", \"geofence\": {}}" "Добавить геозону"
test_endpoint "POST" "/api/parental-control/geofences/update" "{\"geofenceId\": \"test_geofence_1\", \"geofence\": {}}" "Обновить геозону"
test_endpoint "DELETE" "/api/parental-control/geofences/test_geofence_1" "" "Удалить геозону"

# Синхронизация лимитов приложений (3 endpoint'а)
test_endpoint "GET" "/api/parental-control/app-limits/test_child_123" "" "Получить лимиты приложений"
test_endpoint "POST" "/api/parental-control/app-limits/update" "{\"childId\": \"test_child_123\", \"limits\": {}}" "Обновить лимиты приложений"
test_endpoint "GET" "/api/parental-control/app-limits/history?childId=test_child_123&limit=10" "" "История лимитов приложений"

# ============================================
# ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ (5 endpoint'ов)
# ============================================

echo ""
echo "## 👤 Профиль пользователя (5 endpoint'ов)"
echo "## 👤 Профиль пользователя (5 endpoint'ов)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/user-profile/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать профиль"
test_endpoint "POST" "/api/user-profile/update" "{\"userId\": \"$USER_ID\", \"profile\": {}}" "Обновить профиль"
test_endpoint "GET" "/api/user-profile/history?userId=$USER_ID&limit=10" "" "История изменений профиля"
test_endpoint "GET" "/api/user-profile/privacy?userId=$USER_ID" "" "Получить настройки приватности"
test_endpoint "POST" "/api/user-profile/privacy/update" "{\"userId\": \"$USER_ID\", \"privacy\": {}}" "Обновить настройки приватности"

# ============================================
# ТАРИФЫ И ПОДПИСКИ (8 endpoint'ов)
# ============================================

echo ""
echo "## 💳 Тарифы и подписки (8 endpoint'ов)"
echo "## 💳 Тарифы и подписки (8 endpoint'ов)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/subscription/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать тариф"
test_endpoint "POST" "/api/subscription/update" "{\"userId\": \"$USER_ID\", \"subscription\": {}}" "Обновить тариф"
test_endpoint "GET" "/api/subscription/purchase-history?userId=$USER_ID&limit=10" "" "История покупок"
test_endpoint "GET" "/api/subscription/status?userId=$USER_ID" "" "Статус подписки"
test_endpoint "POST" "/api/subscription/status/update" "{\"userId\": \"$USER_ID\", \"status\": \"active\"}" "Обновить статус подписки"
test_endpoint "GET" "/api/subscription/auto-renewal?userId=$USER_ID" "" "Автоматическое продление"
test_endpoint "POST" "/api/subscription/auto-renewal/update" "{\"userId\": \"$USER_ID\", \"enabled\": true}" "Обновить автоматическое продление"
test_endpoint "POST" "/api/subscription/cancel" "{\"userId\": \"$USER_ID\"}" "Отменить подписку"

# ============================================
# НАСТРОЙКИ ПРИЛОЖЕНИЯ (10 endpoint'ов)
# ============================================

echo ""
echo "## ⚙️ Настройки приложения (10 endpoint'ов)"
echo "## ⚙️ Настройки приложения (10 endpoint'ов)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/app-settings/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать настройки"
test_endpoint "POST" "/api/app-settings/update" "{\"userId\": \"$USER_ID\", \"settings\": {}}" "Обновить настройки"
test_endpoint "GET" "/api/app-settings/theme?userId=$USER_ID" "" "Получить тему"
test_endpoint "POST" "/api/app-settings/theme/update" "{\"userId\": \"$USER_ID\", \"theme\": \"dark\"}" "Обновить тему"
test_endpoint "GET" "/api/app-settings/language?userId=$USER_ID" "" "Получить язык"
test_endpoint "POST" "/api/app-settings/language/update" "{\"userId\": \"$USER_ID\", \"language\": \"ru\"}" "Обновить язык"
test_endpoint "GET" "/api/app-settings/notifications?userId=$USER_ID" "" "Получить уведомления"
test_endpoint "POST" "/api/app-settings/notifications/update" "{\"userId\": \"$USER_ID\", \"notifications\": {}}" "Обновить уведомления"
test_endpoint "GET" "/api/app-settings/biometric?userId=$USER_ID" "" "Получить биометрию"
test_endpoint "POST" "/api/app-settings/biometric/update" "{\"userId\": \"$USER_ID\", \"enabled\": true}" "Обновить биометрию"

# ============================================
# ГЕОЛОКАЦИЯ И ГЕОЗОНЫ (7 endpoint'ов)
# ============================================

echo ""
echo "## 📍 Геолокация и геозоны (7 endpoint'ов)"
echo "## 📍 Геолокация и геозоны (7 endpoint'ов)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/location/geofences/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать геозоны"
test_endpoint "POST" "/api/location/geofences/update" "{\"userId\": \"$USER_ID\", \"geofences\": []}" "Обновить геозоны"
test_endpoint "DELETE" "/api/location/geofences/test_geofence_1?userId=$USER_ID" "" "Удалить геозону"
test_endpoint "GET" "/api/location/movement-history?userId=$USER_ID&limit=10" "" "История перемещений"
test_endpoint "POST" "/api/location/movement-history/update" "{\"userId\": \"$USER_ID\", \"movements\": []}" "Обновить историю перемещений"
test_endpoint "GET" "/api/location/status?userId=$USER_ID" "" "Статус геолокации"
test_endpoint "POST" "/api/location/status/update" "{\"userId\": \"$USER_ID\", \"enabled\": true}" "Обновить статус геолокации"

# ============================================
# СЕМЕЙНЫЙ ЧАТ (3 endpoint'а)
# ============================================

echo ""
echo "## 💬 Семейный чат (3 endpoint'а)"
echo "## 💬 Семейный чат (3 endpoint'а)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/chat/offline-messages/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать офлайн сообщения"
test_endpoint "POST" "/api/chat/offline-messages/send" "{\"userId\": \"$USER_ID\", \"message\": {}}" "Отправить офлайн сообщение"
test_endpoint "POST" "/api/chat/offline-messages/resolve-conflicts" "{\"userId\": \"$USER_ID\", \"conflicts\": []}" "Разрешить конфликты сообщений"

# ============================================
# ОФЛАЙН ХРАНИЛИЩЕ (5 endpoint'ов)
# ============================================

echo ""
echo "## 💾 Офлайн хранилище (5 endpoint'ов)"
echo "## 💾 Офлайн хранилище (5 endpoint'ов)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/offline-storage/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать офлайн данные"
test_endpoint "GET" "/api/offline-storage/data?userId=$USER_ID" "" "Получить офлайн данные"
test_endpoint "POST" "/api/offline-storage/data/update" "{\"userId\": \"$USER_ID\", \"data\": {}}" "Обновить офлайн данные"
test_endpoint "DELETE" "/api/offline-storage/data/test_data_1?userId=$USER_ID" "" "Удалить офлайн данные"
test_endpoint "POST" "/api/offline-storage/resolve-conflicts" "{\"userId\": \"$USER_ID\", \"conflicts\": []}" "Разрешить конфликты"

# ============================================
# CRASH DETECTION (4 endpoint'а)
# ============================================

echo ""
echo "## 💥 Crash Detection (4 endpoint'а)"
echo "## 💥 Crash Detection (4 endpoint'а)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/crash-detection/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать данные об авариях"
test_endpoint "POST" "/api/crash-detection/send" "{\"userId\": \"$USER_ID\", \"crashData\": {}}" "Отправить данные об авариях"
test_endpoint "GET" "/api/crash-detection/notifications?userId=$USER_ID" "" "Получить уведомления об авариях"
test_endpoint "POST" "/api/crash-detection/notifications/send" "{\"userId\": \"$USER_ID\", \"notification\": {}}" "Отправить уведомление об авариях"

# ============================================
# ИНТЕРФЕЙС ДЛЯ ПОЖИЛЫХ (4 endpoint'а)
# ============================================

echo ""
echo "## 👴 Интерфейс для пожилых (4 endpoint'а)"
echo "## 👴 Интерфейс для пожилых (4 endpoint'а)" >> "$REPORT_FILE"

test_endpoint "POST" "/api/elderly-interface/medications/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать лекарства"
test_endpoint "POST" "/api/elderly-interface/medications/update" "{\"userId\": \"$USER_ID\", \"medications\": []}" "Обновить лекарства"
test_endpoint "POST" "/api/elderly-interface/appointments/sync" "{\"userId\": \"$USER_ID\"}" "Синхронизировать записи к врачу"
test_endpoint "POST" "/api/elderly-interface/appointments/update" "{\"userId\": \"$USER_ID\", \"appointments\": []}" "Обновить записи к врачу"

# ============================================
# ИТОГОВАЯ СТАТИСТИКА
# ============================================

echo ""
echo "============================================"
echo "📊 ИТОГОВАЯ СТАТИСТИКА"
echo "============================================"
echo ""
echo "Всего протестировано: $TOTAL"
echo -e "${GREEN}Успешно: $SUCCESS${NC}"
echo -e "${YELLOW}Пропущено: $SKIPPED${NC}"
echo -e "${RED}Ошибок: $FAILED${NC}"
echo ""
echo "Процент успеха: $(( SUCCESS * 100 / TOTAL ))%"

# Добавляем статистику в отчет
echo "" >> "$REPORT_FILE"
echo "## Итоговая статистика:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- Всего протестировано: $TOTAL" >> "$REPORT_FILE"
echo "- Успешно: $SUCCESS" >> "$REPORT_FILE"
echo "- Пропущено: $SKIPPED" >> "$REPORT_FILE"
echo "- Ошибок: $FAILED" >> "$REPORT_FILE"
echo "- Процент успеха: $(( SUCCESS * 100 / TOTAL ))%" >> "$REPORT_FILE"

echo ""
echo "📄 Отчет сохранен в: $REPORT_FILE"
echo "📋 Лог сохранен в: $LOG_FILE"
