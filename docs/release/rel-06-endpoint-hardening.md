# rel-06 endpoint hardening (final)

## What was hardened
- Wildcard guard in `main.py` expanded to critical API families:
  - `reports/*`
  - `family/*`
  - `parental/*`
  - `components/*`
- Unknown routes in these families now return explicit `404` and do not go through wildcard -> SFM execution.

## Runtime validation (:8002)
- Service health: `GET /api/health` -> `200`.
- Known critical routes remain functional/protected:
  - `/api/reports/dark-web/stats` -> `200`, `source: api_db`
  - `/api/parental/bypass/stats` -> auth-protected (`403` without token)
  - `/api/components/status` -> auth-protected (`403` without token)
  - `/api/family/members` -> auth-protected (`403` without token)
- Unknown critical routes blocked explicitly:
  - `/api/reports/__unknown__` -> `404`
  - `/api/parental/__unknown__` -> `404`
  - `/api/components/__unknown__` -> `404`
  - `/api/family/__unknown__` -> `404`
- No mock/compat markers found in checked responses (`sfm_mock/sfm_fallback/sfm_error/mock_fallback/reports_compat`).

## Artifacts
- `docs/release/gates/rel-06-hardening-report.json`
- `docs/release/gates/anti-mock-report.json`

## Result
- `rel-06` -> **PASS**
