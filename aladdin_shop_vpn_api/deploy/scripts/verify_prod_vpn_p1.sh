#!/usr/bin/env bash
# P1-WG: проверка timer воркера, env post-expire, наличие скриптов (запуск на VPS).
set -euo pipefail

echo "=== aladdin-shop-vpn-worker.timer ==="
systemctl is-active aladdin-shop-vpn-worker.timer 2>/dev/null || echo "timer: missing/inactive"
systemctl list-timers --all 2>/dev/null | grep -E 'vpn-worker|NEXT' || true

echo "=== env (grep) ==="
ENV_FILE="${VPN_ENV_FILE:-/opt/aladdin-shop-vpn-api/env}"
if [[ -f "$ENV_FILE" ]]; then
  grep -E 'VPN_WG_POST_EXPIRE|VPN_XRAY_POST_EXPIRE|VPN_SUB_ACCESS_ALERT' "$ENV_FILE" || echo "(no matching keys)"
else
  echo "missing $ENV_FILE"
fi

echo "=== scripts executable ==="
for s in wg-peer-down.sh xray-peer-down.sh xray-peer-up.sh; do
  p="/opt/aladdin-shop-vpn-api/deploy/scripts/$s"
  if [[ -x "$p" ]]; then echo "OK $p"; else echo "MISSING or not +x: $p"; fi
done

echo "=== wg0 ==="
ip link show wg0 2>/dev/null | head -1 || echo "wg0 not up"

echo "=== nginx /sub/ rate limit (if configured) ==="
nginx -T 2>/dev/null | grep -A2 'location \^~ /sub/' || echo "(no /sub/ location in nginx -T)"

echo "=== done ==="
