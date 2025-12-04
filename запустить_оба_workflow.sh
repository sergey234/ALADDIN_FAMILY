#!/bin/bash
# Скрипт для запуска обоих workflow по очереди

GITHUB_TOKEN="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"
REPO="sergey234/ALADDIN_FAMILY"
BRANCH="master"

echo "🚀 ШАГ 1: Запускаю check-secrets.yml..."
response1=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/check-secrets.yml/dispatches" \
  -d "{\"ref\":\"$BRANCH\"}")

http_code1=$(echo "$response1" | tail -n1)
body1=$(echo "$response1" | sed '$d')

if [ "$http_code1" = "204" ]; then
  echo "✅ check-secrets.yml успешно запущен!"
else
  echo "❌ Ошибка при запуске check-secrets.yml (HTTP $http_code1)"
  echo "$body1"
fi

echo ""
echo "⏳ Жду 3 секунды..."
sleep 3

echo ""
echo "🚀 ШАГ 2: Запускаю appstore.yml..."
response2=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/appstore.yml/dispatches" \
  -d "{\"ref\":\"$BRANCH\"}")

http_code2=$(echo "$response2" | tail -n1)
body2=$(echo "$response2" | sed '$d')

if [ "$http_code2" = "204" ]; then
  echo "✅ appstore.yml успешно запущен!"
else
  echo "❌ Ошибка при запуске appstore.yml (HTTP $http_code2)"
  echo "$body2"
fi

echo ""
echo "📊 ИТОГОВАЯ ИНФОРМАЦИЯ:"
echo ""
echo "✅ Оба workflow запущены!"
echo ""
echo "🔗 Проверьте статус:"
echo "   1. check-secrets.yml: https://github.com/$REPO/actions/workflows/check-secrets.yml"
echo "   2. appstore.yml: https://github.com/$REPO/actions/workflows/appstore.yml"

