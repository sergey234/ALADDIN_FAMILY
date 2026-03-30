# rel-05 ingest/backfill audit

## Scope
- Validate operational ingest path for 5 analytics domains via real endpoints.
- Validate idempotent write behavior and freshness updates.

## Evidence
- Event replay executed on production gateway `:8002`:
  - `POST /api/reports/identity-theft/allow`
  - `POST /api/reports/privacy/location/allow`
  - `POST /api/reports/privacy/tracker/whitelist`
  - `POST /api/reports/privacy/cleanup/start`
  - `POST /api/reports/dark-web/scan/start`
- All responses: `{"success":true,"data":true,...}`

## Freshness before replay
- darkweb: ~4970s
- identity: ~5665s
- tracker: ~5665s
- location: ~5665s
- cleanup: ~5665s

## Freshness after replay (after exporter cycle)
- darkweb: ~58s
- identity: ~58s
- tracker: ~58s
- location: ~58s
- cleanup: ~58s

## Result
- Operational ingest/write path is functioning for audited 5 domains.
- Backfill/replay mechanism updates domain freshness correctly.
- Domain freshness alerts should remain clear after replay under normal conditions.

## Remaining for full 42/138
- Extend same replay/idempotency pattern to non-audited components/functions.
- Add per-function before/after SQL assertions for full matrix.
