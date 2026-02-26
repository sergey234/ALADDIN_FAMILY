#!/bin/bash
BASE_URL="http://149.154.65.180:8002"

# Получаем токен
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" -H "Content-Type: application/json" -d '{"device_id":"production_check_device"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Не удалось получить токен!"
    exit 1
fi

echo "🔑 Токен получен"

check() {
    local name=$1
    local url=$2
    resp=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL$url" -H "Authorization: Bearer $TOKEN")
    if [ "$resp" == "200" ]; then
        echo "✅ $name: OK"
    else
        echo "❌ $name: $resp"
    fi
}

check "Parental Control" "/api/v1/parental-control/stats?childId=child_masha"
check "Dark Web" "/api/dark-web/status"
check "Identity Theft" "/api/identity-theft/status"
check "Location Bubble" "/api/location-bubble/status"
check "Notifications" "/api/notifications/status"
check "Crash Detection" "/api/crash-detection/status"
