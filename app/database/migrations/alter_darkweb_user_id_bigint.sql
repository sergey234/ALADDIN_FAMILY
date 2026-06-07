-- JWT user_id can exceed INTEGER max — widen scope columns.
-- Apply: sudo -u postgres psql -d aladdin_db -f alter_darkweb_user_id_bigint.sql

ALTER TABLE darkweb.scan_events
    ALTER COLUMN user_id TYPE BIGINT;

ALTER TABLE darkweb.darkweb_leaks
    ALTER COLUMN user_id TYPE BIGINT;
