# Runbook — Antifake worker OOM + SFM 422 (P-03)

**Links:** `RUNBOOK_SFM_ML_DEGRADED.md` (P-06) · `RUNBOOK_ANTIFAKE_MODEL_VERSION.md` (F-07) · F-01 acceptance (no mock sources)

**Host:** `149.154.65.180` · API `:8002` · SFM `:8003` · Worker `aladdin-antifake-worker.service`

---

## Symptoms

| Signal | Likely cause |
|--------|----------------|
| Media jobs stuck `queued` / `processing` | Worker down, OOM killed, Redis unavailable |
| `journalctl` worker: `Killed` / OOM | RAM exhausted on audio/video verify |
| SFM `422` / `active_executions` | Slot leak in SFM execute path |
| Smoke: job timeout, `failed` status | Worker or SFM not completing |
| P-02 alert: queue depth > 50 | Backlog — scale worker or fix upstream |

---

## Triage (5 min)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
systemctl is-active aladdin-antifake-worker.service aladdin-backend.service aladdin-sfm-core.service
journalctl -u aladdin-antifake-worker -n 60 --no-pager
journalctl -u aladdin-sfm-core -n 40 --no-pager | grep -E '422|OOM|Killed|active_executions' || true
cd /opt/aladdin-backend && ./venv/bin/python3 scripts/antifake_ops_alerts.py --check-all
free -h
```

---

## Worker OOM

1. **Restart worker** (clears stuck RQ jobs in processing state may need manual fail):
   ```bash
   systemctl restart aladdin-antifake-worker.service
   sleep 3
   systemctl is-active aladdin-antifake-worker.service
   ```
2. **Check Redis queue** — if depth still high after restart, inspect failed jobs in `antifake_jobs`:
   ```sql
   SELECT status, COUNT(*) FROM antifake_jobs
   WHERE updated_at > NOW() - INTERVAL '1 hour'
   GROUP BY status;
   ```
3. **Reduce load** — temporary: set `ANTIFAKE_ASYNC_MEDIA=false` in `.env` (sync path, slower but no queue backlog). Restart API only after change.
4. **Re-verify:**
   ```bash
   ANTIFAKE_SMOKE_POLL_JOB=1 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py
   ./venv/bin/python3 scripts/antifake_verify_worker.py
   ```

**Do not** return mock/`sfm_mock` sources — F-01 requires 503 or honest `local_ml`/`real_agent`.

---

## SFM 422 / active_executions

1. Restart SFM (F-01 purge on boot):
   ```bash
   systemctl restart aladdin-sfm-core.service
   sleep 16
   curl -s http://127.0.0.1:8003/api/sfm/status | jq .
   ```
2. If 422 persists — full sequence in `RUNBOOK_SFM_ML_DEGRADED.md` (restart API + worker after SFM healthy).
3. Golden text smoke must pass Q-06 (`real_agent` or acceptable `local_ml`).

---

## F-01 acceptance after recovery

- [ ] `test_antifake_prod_smoke.py` green with `ANTIFAKE_SMOKE_POLL_JOB=1`
- [ ] `antifake_prod_gate_af11.py` green
- [ ] No `sfm_mock` / `mock-real-protection` in API responses
- [ ] P-01 job failure rate < 5% (or sample too small)
- [ ] P-02 queue depth ≤ 50

---

## Escalation

- RAM consistently < 500MB free during media jobs → upgrade VPS or cap concurrent media (ops ticket).
- Repeated OOM after deploy → rollback code: `RUNBOOK_ANTIFAKE_DEPLOY_ROLLBACK.md`
- Bad fraud DB ingest flooding labels → `RUNBOOK_ANTIFAKE_SCAM_DB_ROLLBACK.md` (P-04)
