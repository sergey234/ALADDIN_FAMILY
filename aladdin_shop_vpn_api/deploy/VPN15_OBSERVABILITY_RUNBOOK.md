# vpn-15 — наблюдаемость vpn-api (Prometheus + Sentry)

**Цель:** снимать метрики с **`aladdin-shop-vpn-api`** для алертов и дашбордов (p95 латентности, RPS, очередь `jobs`, счётчики аккаунтов по статусам). **Sentry** — ошибки и трейсы; **Prometheus** — операционные SLO.

---

## 1. Эндпоинт

| Метод | Путь | Формат |
|-------|------|--------|
| GET | `/metrics` | Prometheus text exposition (`Content-Type` из `prometheus_client`) |

**Важно:** не открывайте `/metrics` в публичный интернет без ACL (IP allowlist, отдельный internal vhost, или только loopback + Prometheus на той же машине).

---

## 2. Что экспортируется (имена метрик)

- **`aladdin_shop_vpn_http_request_duration_seconds`** — `Histogram`, labels `method`, `route` (маршруты нормализованы: `/sub/*`, целые internal/legal пути).
- **`aladdin_shop_vpn_http_requests_total`** — `Counter`, labels `method`, `route`, `status_class` (`2xx`…`5xx`).
- **Gauges из `vpn.db`** (обновляются при каждом scrape `/metrics`):
  - `aladdin_shop_vpn_jobs_{pending,processing,failed,done}`
  - `aladdin_shop_vpn_accounts_vpn_{active,provisioning,expired,failed,manual_override}`

Запрос к **`/metrics`** сам не попадает в histogram/counter (избегаем шума).

---

## 3. Prometheus: scrape

Пример **`scrape_configs`** (uvicorn на **8091** только с localhost; подставьте job/instance под свою инвентаризацию):

```yaml
scrape_configs:
  - job_name: aladdin-shop-vpn-api
    metrics_path: /metrics
    static_configs:
      - targets: ["127.0.0.1:8091"]
        labels:
          service: aladdin-shop-vpn-api
          env: production
```

Проверка с VPS:

```bash
curl -sS "http://127.0.0.1:8091/metrics" | head -n 40
```

---

## 4. p95 по HTTP (PromQL)

Пример для всех маршрутов (подстройте `5m` под частоту трафика):

```promql
histogram_quantile(
  0.95,
  sum by (le, route, method) (
    rate(aladdin_shop_vpn_http_request_duration_seconds_bucket[5m])
  )
)
```

Для **`POST /internal/v1/provision`**:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(aladdin_shop_vpn_http_request_duration_seconds_bucket{route="/internal/v1/provision",method="POST"}[5m])
  )
)
```

---

## 4.1 Alertmanager (systemd на Ubuntu)

Имя unit: **`prometheus-alertmanager.service`** (не `alertmanager.service`).

```bash
systemctl status prometheus-alertmanager
curl -sS http://127.0.0.1:9093/-/healthy
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/fix_alertmanager_telegram.py
```

Скрипт читает `ALERT_TELEGRAM_*` из `/opt/aladdin-telegram-shop-bot/shared/.env`, пишет `/etc/prometheus/alertmanager.yml`, включает `alerting:` в Prometheus.

---

## 5. Grafana

Импортируемый дашборд (панели p95, RPS, gauges): **`deploy/grafana/aladdin_shop_vpn_api_dashboard.json`**.

После импорта выберите datasource **Prometheus** в переменной дашборда.

---

## 6. nginx (опционально): отдельный internal location

Если по ошибке `/metrics` проброшен наружу через тот же server — ограничьте доступ. Пример: **`deploy/nginx_vpn_metrics_allow_local.conf.example`**.

---

## 7. Sentry

Переменные: **`SENTRY_DSN`**, **`SENTRY_ENVIRONMENT`**, **`SENTRY_TRACES_SAMPLE_RATE`** (см. `aladdin_shop_vpn_api` settings / `VPN_SHOP_API.md`).

## 8. Alertmanager → Telegram (доставка алертов)

Правила в `/etc/prometheus/alert_rules.yml` (в т.ч. `AladdinShopVpnApiDown`) **не шлют** сообщения сами — нужны:

1. Блок `alerting:` в `/etc/prometheus/prometheus.yml` → `127.0.0.1:9093`
2. Рабочий **`prometheus-alertmanager.service`**
3. Receiver **telegram-ops** в `/etc/prometheus/alertmanager.yml` (`ALERT_TELEGRAM_*` из `shared/.env` бота)

Одноразовая починка на проде:

```bash
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/fix_alertmanager_telegram.py
```

Типичная ошибка single-node: gossip cluster — в `/etc/default/prometheus-alertmanager` задать `--cluster.listen-address=""`.

Проверка:

```bash
systemctl is-active prometheus-alertmanager prometheus
curl -sS http://127.0.0.1:9093/-/healthy
curl -sS http://127.0.0.1:9090/api/v1/alertmanagers | head
```

---

## 8. После деплоя: единый каталог локаций и инструкции

Чтобы **vpn-api** и бот показывали один и тот же список локаций:

1. На сервере vpn-api в **`shared/.env`** (или env unit) задайте тот же **`VPN_LOCATIONS_JSON`**, что и у бота.
2. В боте для каталога из API: **`VPN_LOCATIONS_FROM_API=true`**.
3. Ссылка на длинные инструкции: **`VPN_INSTRUCTIONS_URL`** (например `https://aladdin-ai.ru/v1/legal/vpn-instructions`).
4. При необходимости **`SENTRY_DSN`** на vpn-api.
5. Перезапуск **`aladdin-shop-vpn-api`** и бота.
