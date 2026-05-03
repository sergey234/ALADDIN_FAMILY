#!/usr/bin/env bash
# Этап 0 (часть «снаружи»): публичный DNS + форма ответа monitoring/detail без JWT.
# Не требует секретов. Для сравнения с origin (localhost:8002 и JWT) — на сервере по гайду деплоя.
# Использование:
#   ./tools/phase0_monitoring_gateway_check.sh
#   ./tools/phase0_monitoring_gateway_check.sh aladdin-ai.ru MEM_B6DCC7194068
set -euo pipefail

HOST="${1:-aladdin-ai.ru}"
CHILD="${2:-MEM_B6DCC7194068}"
PATH_Q="/api/parental-control/monitoring/detail?childId=${CHILD}"
URL="https://${HOST}${PATH_Q}"

echo "== dig +short ${HOST}"
if command -v dig >/dev/null 2>&1; then
  dig +short "${HOST}" | sed 's/^/  /' || true
else
  echo "  (dig не установлен — пропуск)"
fi

echo "== GET ${URL}"
TMP="$(mktemp)"
CODE="$(curl -sS -m 20 -o "${TMP}" -w "%{http_code}" "${URL}")"
BODY="$(cat "${TMP}")"
rm -f "${TMP}"
echo "${BODY}" | jq . 2>/dev/null || echo "${BODY}"
echo "(HTTP ${CODE})"
echo ""

# После выката FastAPI-роутера без JWT ожидаемо 401/403 с полем detail — это НЕ envelope-заглушка.
if [[ "${CODE}" == "401" || "${CODE}" == "403" ]] && echo "${BODY}" | jq -e '.detail != null' >/dev/null 2>&1; then
  echo "VERDICT: до FastAPI доходит реальный роутер (требуется JWT); envelope/mock на этом пути снят."
  exit 0
fi

if echo "${BODY}" | jq -e '.top_sites != null' >/dev/null 2>&1; then
  echo "VERDICT: контракт FastAPI (есть top_sites) — публичный шлюз OK для этого пути."
  exit 0
fi

if echo "${BODY}" | jq -e '.function != null' >/dev/null 2>&1; then
  echo "VERDICT: envelope/mock (есть function, нет top_sites) — см. docs/PARENTAL_MONITORING_DETAIL_GATEWAY_PLAN.md (wildcard SFM или неверный upstream)."
  exit 2
fi

echo "VERDICT: неожиданное тело (нет top_sites, не envelope, не стандартная 401/403)."
exit 1
