# Data Map Snapshot (G21-G23)

## Data Domains

| Domain | Source | Storage | Sync | Protection |
|---|---|---|---|---|
| Child content progress | App interaction | Local app storage/content DB | Optional background sync | App sandbox + validation |
| Family roster/profile | API (`family`, profile endpoints) | Local profile store | Two-way reconcile with strategy | Access policy checks + versioning |
| Parent dashboard metrics | Aggregated local + API-backed signals | In-memory + export files | On-demand refresh | Parent session gate for sensitive actions |
| Localization resources | Repo strings files | App bundle | CI parity checks | Lint + placeholder parity |
| Compliance artifacts | CI scripts/reports | `docs/` artifacts | Generated per run | Review sign-off process |

## Sensitive Data Controls

- PII never committed in plain logs/evidence docs.
- DSAR and deletion operations remain parent-gated.
- Session-sensitive actions require parent confirmation where configured.

## Evidence References

- `docs/PHASE8_SECURITY_VALIDATION.md`
- `docs/TRACKB_PRIVACY_COMPLIANCE_GATE.md`
- `docs/THREAT_MODEL_DELTA_G21_G23.md`
- `docs/DSAR_SCREENSHOTS_LOG_G21_G23.md`

