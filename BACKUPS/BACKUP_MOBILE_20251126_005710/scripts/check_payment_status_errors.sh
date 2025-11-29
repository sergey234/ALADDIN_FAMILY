#!/bin/bash
THRESHOLD=10
COUNT=$(journalctl -u payment_service --since "15 minutes ago" --no-pager | grep "/api/payments/status" | egrep "404|500" | wc -l)

if [ "$COUNT" -ge "$THRESHOLD" ]; then
  MESSAGE="[ALERT] payment_service: $COUNT errors in last 15 minutes"
  echo "$MESSAGE" | mail -s "payment_service alert" admin@example.com
  # Пример для Telegram:
  # curl -s -X POST "https://api.telegram.org/botTOKEN/sendMessage" \
  #   -d "chat_id=CHAT_ID" \
  #   -d "text=$MESSAGE" > /dev/null
fi


