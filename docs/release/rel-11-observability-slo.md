# rel-11 observability + SLO gate

## Verified
- Gateway metrics present on `:8002/metrics`:
  - `http_requests_total`
  - `http_request_duration_seconds_bucket`
  - `aladdin_analytics_freshness_seconds`
- Prometheus rules loaded (`/api/v1/rules`):
  - `AladdinNoFreshDataByDomain`
  - `AladdinAPILatencyP95High`
  - `Aladdin5xxRateSpike`
  - threshold recording rules by domain
- Prometheus target health (`/api/v1/targets`): `gateway` target is `up`.
- Prometheus active alerts (`/api/v1/alerts`): none active.

## SLO checks (from Prometheus API)
- p95 latency `< 0.5s` -> PASS (`~0.0475s`)
- 5xx share `< 1%` -> PASS (`0`)
- freshness per domain within thresholds -> PASS
- no active alerts -> PASS

## Artifact
- `docs/release/gates/observability-slo-report.json`

## Note
- Alertmanager API `:9093` is not reachable from current host check, but alert states are validated directly via Prometheus (`/api/v1/alerts`) and rule loading is confirmed.

## Status
- `rel-11`: **PASS**
