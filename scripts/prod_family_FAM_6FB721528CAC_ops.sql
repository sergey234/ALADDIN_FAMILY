-- ALADDIN prod: family FAM_6FB721528CAC — table public.family_members (verified 2026-05-04)
-- Run ONLY after backup. SSH + restart: ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md
--
-- Full data-only dump (example; run on server as postgres user):
--   mkdir -p /opt/aladdin-backend/backups && sudo -u postgres pg_dump -d aladdin_db \
--     -t public.family_members -t public.families --data-only --inserts \
--     -f /opt/aladdin-backend/backups/aladdin_family_tables_$(date +%Y%m%d_%H%M%S).sql

-- Read-only audit
-- SELECT id, family_id, user_id, name, role, status FROM family_members WHERE family_id = 'FAM_6FB721528CAC' ORDER BY created_at;

-- Applied on prod 2026-05-04: sole member was incorrectly `child`; restored parent role for creator roster UX.
-- UPDATE family_members SET role = 'parent', updated_at = CURRENT_TIMESTAMP
--   WHERE family_id = 'FAM_6FB721528CAC' AND id = 'MEM_8D89E154' AND role = 'child';

-- If API still returns wrong capability, next step is binding user_id for this membership row from JWT subject
-- and/or implementing backend reconcile (no single child without parent when tariff allows >1).
