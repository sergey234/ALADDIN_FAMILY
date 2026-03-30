# Handoff: Ownership, Artifacts, SLO/SLA

## Ownership
- Backend runtime/API routing: backend team (gateway + routers)
- DB schema/grants/migrations: backend + DB owner
- iOS endpoint contract sync: mobile team
- Observability (Prometheus/Alertmanager/Grafana): SRE/ops owner

## Key Artifacts
- Unified architecture report:
  - `docs/release/ALADDIN_ML_SYSTEM_42x138_ARCHITECTURE_AND_EXECUTION_REPORT.md`
- Gate outputs:
  - `docs/release/release-gate-report.json`
  - `docs/release/go-no-go.md`
  - `docs/release/gates/*.json`
- Soak outputs:
  - `docs/release/soak/*.samples.jsonl`
  - `docs/release/soak/*.summary.json`

## SLO/SLA Targets (Operational)
- API p95 latency: `< 0.5s`
- 5xx share: `< 1%`
- Freshness thresholds:
  - darkweb `<= 72h`
  - identity `<= 24h`
  - tracker `<= 12h`
  - location `<= 6h`
  - cleanup `<= 168h`

## Release Decision Policy
- GO only if all gates PASS, including `rel-15` soak.
- Any critical blocker => NO_GO.

## Operational Notes
- Primary production runtime is `:8002`.
- For no-hang operations use short-step commands + explicit timeout wrappers.
- Validate business effect, not just HTTP 200 (SQL before/after for write endpoints).
