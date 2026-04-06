#!/usr/bin/env bash
set -euo pipefail

# Nightly reconcile job for family_members table.
# Clears conflicting user_id for non-parent roles and normalizes invalid statuses.
# Runs directly against PostgreSQL to avoid API auth requirements for bulk maintenance.
#
# Expected environment on server:
#   - PostgreSQL local instance with database 'aladdin_db'
#   - psql available and superuser via sudo -u postgres
#
# Logs: stdout/stderr should be redirected by cron to a file.

echo "[INFO] $(date -Iseconds) Nightly family reconcile started"

PSQL="sudo -u postgres psql -v ON_ERROR_STOP=1 -d aladdin_db -c"

# Ensure expected table exists before running fixes
HAS_TABLE=$(sudo -u postgres psql -At -d aladdin_db -c "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='family_members');" | tr -d '[:space:]')
if [[ "${HAS_TABLE}" != "t" ]]; then
  echo "[WARN] family_members table not found; skipping"
  exit 0
fi

echo "[INFO] Applying non-parent user_id conflict cleanup"
${PSQL} "
UPDATE public.family_members fm
SET user_id = NULL
WHERE user_id IS NOT NULL
  AND lower(COALESCE(role,'')) <> 'parent'
  AND EXISTS (
    SELECT 1
    FROM public.family_members p
    WHERE p.family_id = fm.family_id
      AND p.user_id = fm.user_id
      AND lower(COALESCE(p.role,'')) = 'parent'
  );
"

echo "[INFO] Normalizing invalid or empty statuses to 'protected'"
${PSQL} "
UPDATE public.family_members
SET status = 'protected'
WHERE COALESCE(lower(status),'') NOT IN ('protected','warning','danger');
"

echo "[INFO] $(date -Iseconds) Nightly family reconcile finished"

