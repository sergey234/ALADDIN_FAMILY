#!/usr/bin/env bash
# ai-sse-nginx: insert dedicated SSE location (idempotent)
set -euo pipefail
CONF="/etc/nginx/sites-enabled/aladdin-ai.ru"
MARKER="# ALADDIN_AI_SSE_STREAM"
if grep -q "$MARKER" "$CONF"; then
  echo "already applied"
  exit 0
fi
TMP=$(mktemp)
awk -v block="$MARKER" '
  /# Основной location для API/ && !done {
    print "    " block
    print "    location /api/ai/assistant/stream {"
    print "        proxy_pass http://127.0.0.1:8002;"
    print "        proxy_http_version 1.1;"
    print "        proxy_set_header Connection \"\";"
    print "        proxy_set_header Host $host;"
    print "        proxy_set_header X-Real-IP $remote_addr;"
    print "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
    print "        proxy_set_header X-Forwarded-Proto $scheme;"
    print "        proxy_buffering off;"
    print "        proxy_cache off;"
    print "        proxy_read_timeout 120s;"
    print "        proxy_send_timeout 120s;"
    print "        chunked_transfer_encoding on;"
    print "    }"
    print ""
    done=1
  }
  { print }
' "$CONF" > "$TMP"
cp "$CONF" "${CONF}.bak-ai-sse-$(date +%Y%m%d%H%M%S)"
mv "$TMP" "$CONF"
nginx -t
systemctl reload nginx
echo "nginx SSE applied OK"
