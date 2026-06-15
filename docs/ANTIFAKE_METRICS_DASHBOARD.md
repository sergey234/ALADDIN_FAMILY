# Antifake metrics dashboard (F-06)

**Endpoint:** `GET /api/antifake/metrics` (Premium JWT)

## Fields

| Field | Description |
|-------|-------------|
| `checks_total` | Completed jobs for user |
| `fake_detected` | Jobs with `verdict=likely_fake` |
| `by_type` | Counts per `text/audio/video/call/document` |
| `latency_p95_ms` | PostgreSQL p95 job latency |
| `avg_latency_ms` | Mean latency |
| `model_version` | `ANTIFAKE_MODEL_VERSION` env (F-07) |
| `sla_ms` | SLA targets for client UX |

## Ops query (all users)

```sql
SELECT job_type, status, COUNT(*), AVG(latency_ms)::int
FROM antifake_jobs
GROUP BY job_type, status;
```

## Grafana / manual

- Poll metrics per smoke user after gate script `scripts/antifake_prod_gate_af11.py`
- **P-01:** job failure > 5% in 60m → `scripts/antifake_ops_alerts.py --check-jobs` (exit 2)
- **P-02:** RQ queue depth > 50 → `scripts/antifake_ops_alerts.py --check-queue` (exit 2)
- Cron on prod: `*/15` → `antifake_ops_alerts.py --check-all` (see `deploy_antifake_m1.sh`)
