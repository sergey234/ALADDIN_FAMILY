# Утверждённые пороги freshness (obs-thresholds-confirm)

Зафиксировано для прод‑наблюдаемости по доменам компонентной аналитики (согласовано с `RUNBOOK_SLO_SLA_OWNERSHIP.md` и планом ML §4.E).

| domain (в `analytics_freshness` / метках Prometheus) | Макс. возраст данных (SLO) |
|--------------------------------------------------------|----------------------------|
| darkweb                                                | 72 часа                    |
| identity                                               | 24 часа                    |
| tracker                                                | 12 часов                   |
| location                                               | 6 часов                    |
| cleanup                                                | 168 часов (7 суток)        |

Дополнительно (цели API, не доменные freshness):

- Latency p95: **500 ms** (окно алерта при включённых HTTP‑метриках — 10 минут).
- Доля 5xx: **1%** (окно — 5 минут).

Экспорт в Prometheus: gauge `aladdin_analytics_freshness_seconds{domain="...",env="...",service="...",version="..."}` (см. `main.py` и `api_gateway.py`, фоновое обновление с периодом 30 с). Порог для алерта: сравнение gauge с доменным SLA (пример правил — `prometheus_aladdin_analytics_alerts.example.yml`).
