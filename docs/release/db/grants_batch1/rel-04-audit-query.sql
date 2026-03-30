-- audit privileges for mapped tables
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee='aladdin_user' AND ((table_schema='cleanup' AND table_name='cleanup_records') OR (table_schema='darkweb' AND table_name='darkweb_leaks') OR (table_schema='identity' AND table_name='identity_attempts') OR (table_schema='location' AND table_name='location_requests') OR (table_schema='public' AND table_name='ai_category_reports') OR (table_schema='public' AND table_name='parental_reports') OR (table_schema='tracker' AND table_name='tracker_blocks'))
ORDER BY table_schema, table_name, privilege_type;
