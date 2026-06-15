# Runbook — Mass false positive scam DB rollback (P-04)

**Table:** `antifake_scam_numbers` · **iOS impact:** Call Directory sync shows wrong labels until clients re-sync.

**Script:** `scripts/antifake_scam_db_rollback.py`

---

## When to use

- Crowd reports (`user_report`) approved in bulk with bad data
- `call_analyze` ingest loop mis-labels legitimate numbers
- Ops mistake during CSV import
- Users report widespread false «мошенник» labels (D-04 QA numbers must stay active)

---

## Before any change

1. **Snapshot** current active set:
   ```bash
   cd /opt/aladdin-backend
   ./venv/bin/python3 scripts/antifake_scam_db_rollback.py snapshot --tag before_rollback_$(date +%Y%m%d)
   ```
2. Note `active_count`:
   ```bash
   ./venv/bin/python3 scripts/antifake_scam_db_rollback.py stats
   ```
3. Ensure QA numbers present (device QA): `backend_tests/test_antifake_call_directory_store.py` / C-11 sources `qa`.

---

## Option A — deactivate by source + time

Use when bad batch has known `source` and `updated_at` window:

```bash
./venv/bin/python3 scripts/antifake_scam_db_rollback.py deactivate-source \
  --source user_report \
  --since 2026-06-15T10:00:00Z
```

Sources: `user_report`, `call_analyze`, `ru_v1`, `csv`, `manual`, `qa`.

---

## Option B — full restore from snapshot

```bash
LATEST=$(ls -1t .deploy_backups/scam_snapshot_before_rollback_*.json | head -1)
./venv/bin/python3 scripts/antifake_scam_db_rollback.py restore --file "$LATEST"
```

---

## After rollback

1. Verify count: `stats` — must stay ≥ 100 for RU seed (C-08) unless restoring known-good snapshot.
2. API check:
   ```bash
   curl -s -H "Authorization: Bearer $TOKEN" \
     "http://127.0.0.1:8002/api/antifake/call-directory" | jq '.total_count'
   ```
3. Ask internal testers to **force sync** in Hub (or wait for delta `since=`).
4. Document incident in `docs/release/qa_signoff/antifake/` if external beta affected.

---

## Prevention

- Moderation queue for I-batch reports before `active=TRUE`
- `MAX_CALL_DIRECTORY_ENTRIES` guard (C-10) — API returns `truncated` when > 50k
- P-01/P-02 alerts — spike in failed jobs may correlate with bad deploy
