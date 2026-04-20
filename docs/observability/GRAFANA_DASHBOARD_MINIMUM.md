# Grafana: минимум панелей (obs-grafana-dashboard)

Имя дашборда в runbook: **`ALADDIN - Gateway & Analytics Observability`** (папка `ALADDIN`).

Минимальный набор панелей (см. также `RUNBOOK_SLO_SLA_OWNERSHIP.md`):

1. **Freshness по доменам** — `aladdin_analytics_freshness_seconds`, легенда по `domain`, линии порогов из `THRESHOLDS_CONFIRMED.md`.
2. **RPS** — по HTTP‑метрикам шлюза (когда включены `http_*` / `prometheus_fastapi_instrumentator`).
3. **Latency p50 / p95** — те же HTTP‑метрики.
4. **Доля 5xx** — отношение 5xx к общему числу ответов по маршрутам `/api/reports/*`.

Переменные дашборда: `env`, `version` (из лейблов `env`, `version` у метрик).
