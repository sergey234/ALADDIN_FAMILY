# Wellness Postgres Migration (p3-11)

> **Статус:** `wellness_store_postgres.py` + `migrate_wellness_sqlite_to_pg.py` + dual-write hooks · prod default SQLite until `WELLNESS_PG_DSN` set.

---

## 1. Scope

Migrate tables:

- `wellness_checkins`, `wellness_assessments`, `wellness_exercises`
- `wellness_outcomes`, `wellness_dreams`, `wellness_insights`
- `wellness_settings`, `wellness_crisis_log`

---

## 2. Encryption at rest

| Column | Policy |
|--------|--------|
| `wellness_checkins.notes` | Fernet / KMS |
| `wellness_dreams.content` | Fernet / KMS |
| `wellness_outcomes.note` | Fernet / KMS |

Env: `WELLNESS_PG_DSN`, `WELLNESS_FIELD_ENCRYPTION_KEY`.

---

## 3. Runbook

1. Snapshot SQLite: `cp companion_store.db companion_store.pre_pg.bak`
2. Set `WELLNESS_PG_DSN=postgresql://...`
3. Run migration: `PYTHONPATH=. python3 scripts/migrate_wellness_sqlite_to_pg.py --dry-run` then without `--dry-run`
4. Enable dual-write: `WELLNESS_PG_DUAL_WRITE=1` in `.env` (SQLite still primary)
5. Cutover reads: `WELLNESS_PG_READ=1` after 7d dual-write window
6. `./scripts/verify_wellness_prod.sh`

**Bootstrap Postgres (VPS/docker):** `./scripts/setup_wellness_postgres_docker.sh`

---

## 4. Health check

`GET /api/wellness/store/backend` → `{ "backend": "postgres", "configured": true }`

---

*Связано: p3-11 · `wellness_store_postgres.py`*
