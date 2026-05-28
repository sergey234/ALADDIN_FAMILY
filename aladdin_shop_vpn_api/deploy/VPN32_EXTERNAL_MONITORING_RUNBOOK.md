# VPN32 — внешний мониторинг (не с того же VPS)

**Зачем:** проверки с `149.154.65.180` не видят блокировку «снаружи» у оператора.

## 1. Что мониторить

| Проверка | URL / порт | Ожидание |
|----------|------------|----------|
| Backend health | `http://149.154.65.180:8002/api/health` | 200 + `ok` |
| Shop Partner API | `https://aladdin-ai.ru/v1/...` или health через nginx | 200 |
| VPN instructions | `https://aladdin-ai.ru/v1/legal/vpn-instructions` | 200 |
| VPN subscription path | HEAD `https://aladdin-ai.ru/sub/` (без токена) | 4xx, не 5xx nginx |
| UDP WG | с внешней сети до `VPN_WG_ENDPOINT_HOST:51820` | optional |

## 2. Инструменты (выберите один+)

- **Uptime Kuma / HetrixTools / Better Stack** — HTTP(S) с разных регионов.
- **Отдельный VPS** (дешёвый) + cron + скрипт `deploy/scripts/external_vpn_smoke.sh`.
- **healthchecks.io** — ping URL раз в N минут.

## 3. Скрипт на внешней машине

```bash
# На НЕ основном VPS, в cron каждые 5 мин (пример: deploy/cron/external_vpn_smoke.cron.example):
ALADDIN_EXTERNAL_SMOKE_URLS="https://aladdin-ai.ru/v1/legal/vpn-instructions,https://aladdin-ai.ru/v1/legal/vpn-terms" \
  /opt/aladdin-shop-vpn-api/deploy/scripts/external_vpn_smoke.sh
```

Проверки: HTTPS 200 на legal; **`/sub/__smoke_unknown__` → 404** (не 502/503 nginx).

Опционально Telegram при FAIL: `ALERT_TELEGRAM_BOT_TOKEN` + `ALERT_TELEGRAM_CHAT_ID` (как у Alertmanager).

**Проверено 2026-05-15** с интернета (не с VPS): все OK.

## 3.1 Регрессия на самом VPS (дополнение, не замена vpn-32)

Timer **`aladdin-vpn-prod-smoke.timer`** (каждые 15 мин) — `vpn_prod_smoke.sh` на loopback. Ловит поломку API; **не** видит блокировку IP снаружи.

## 4. Связка с Alertmanager

Внутренние алерты Prometheus (**vpn-15**) дополняют, но **не заменяют** внешний HTTP-check: при блокировке IP снаружи внутренний `up{job="aladdin-shop-vpn-api"}` может оставаться 1.
