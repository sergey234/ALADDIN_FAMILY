# ALADDIN Observability Runbook (SLO/SLA/Ownership)

## Scope

This runbook covers production observability for the analytics/reporting domains:

- darkweb
- identity
- tracker
- location
- cleanup

It applies to:

- gateway metrics endpoint (`/metrics`)
- Prometheus scrape/rules
- Alertmanager routing
- Grafana dashboard `ALADDIN - Gateway & Analytics Observability`

## Ownership

- **Primary owner (L1):** Backend on-call (ALADDIN API)
- **Secondary owner (L2):** Data/Analytics pipeline owner
- **Escalation (L3):** Platform/SRE owner
- **Business escalation:** Product owner for Security/ML system

## SLO / SLA Targets

- **Availability (gateway reports endpoints):** >= 99.9% monthly
- **Freshness SLO by domain:**
  - darkweb <= 72h
  - identity <= 24h
  - tracker <= 12h
  - location <= 6h
  - cleanup <= 168h
- **API latency SLO (target):** p95 < 500ms
- **Server errors SLO (target):** 5xx rate < 1%

Current production alert rules are active for freshness. Latency/5xx alerts should be enabled after HTTP metrics instrumentation is fully available.

## Active Alerts

- `AladdinNoFreshDataByDomain`
  - Expression:
    - `aladdin_analytics_freshness_seconds > on(domain) group_left() aladdin_analytics_freshness_threshold_seconds`
  - For: `15m`
  - Severity: `warning`

## Required Dashboards

- Grafana folder: `ALADDIN`
- Dashboard: `ALADDIN - Gateway & Analytics Observability`
- Minimum panels:
  - freshness per domain
  - requests per second (RPS)
  - latency p50/p95
  - 5xx rate

## Incident Response Playbooks

### 1) Freshness alert fired

Symptoms:

- Alert: `AladdinNoFreshDataByDomain`
- One or more domains breach freshness threshold

Checks:

1. Gateway metrics:
   - `curl -s http://localhost:8002/metrics | grep aladdin_analytics_freshness_seconds`
2. Prometheus query:
   - `curl -s 'http://localhost:9090/api/v1/query?query=aladdin_analytics_freshness_seconds'`
3. Source DB view:
   - `SELECT * FROM analytics_freshness;`
4. Ingestion health:
   - verify consumers/cron/backfill pipeline status

Recovery:

1. Restore ingestion flow for affected domain
2. Validate DB writes for latest events
3. Confirm gauge updates in `/metrics`
4. Confirm alert transitions `firing -> resolved`

Exit criteria:

- Domain freshness returns below threshold for at least 15 minutes.

### 2) Prometheus target down

Symptoms:

- `gateway` target is `down`
- missing metrics in dashboard

Checks:

1. `systemctl status prometheus`
2. `curl -s http://localhost:9090/-/ready`
3. `curl -s http://localhost:9090/api/v1/targets`
4. `curl -s http://localhost:8002/metrics`

Recovery:

1. Fix gateway process / port / firewall / DNS
2. Restart services if required:
   - `systemctl restart prometheus`
   - restart gateway process
3. Re-check target health `up`

Exit criteria:

- target `gateway` is `up`, data visible in Prometheus and Grafana.

### 3) High p95 or 5xx (after HTTP metrics are enabled)

Checks:

1. Verify HTTP metric presence:
   - `http_requests_total`
   - `http_request_duration_seconds_bucket`
2. Correlate with release timeline and recent deploys
3. Check gateway logs for errors/timeouts

Recovery:

1. Roll back problematic release if needed
2. Reduce load / disable problematic route
3. Optimize DB query hotspots

Exit criteria:

- p95 and 5xx stabilize under thresholds for 10+ minutes.

## PII / Security Guardrails

- No raw PII in metric labels
- Keep labels low-cardinality (`domain`, `env`, `service`, `version`)
- DB metrics reads must use read-only access where possible
- Logs must remain masked for sensitive fields

## Verification Checklist (Post-change)

1. Prometheus:
   - service active
   - rules loaded
   - gateway target `up`
2. Alertmanager:
   - service active
   - route/receiver config valid
3. Grafana:
   - datasource reachable
   - dashboard loads
4. Freshness:
   - all 5 domain series present
5. Compat/mock:
   - no `reports_compat|sfm_mock|mock_fallback` in critical responses

## Periodic Operations

- Daily:
  - check active alerts
  - verify freshness values per domain
- Weekly:
  - review SLO error budget
  - verify alert noise/flapping
- Release-time:
  - run smoke checks for 5 stats + 5 list endpoints
  - confirm no mock markers

