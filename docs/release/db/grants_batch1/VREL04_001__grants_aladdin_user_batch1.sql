-- rel-04 least-privilege grants batch-1 for aladdin_user
BEGIN;
GRANT USAGE ON SCHEMA cleanup, darkweb, identity, location, public, tracker TO aladdin_user;
GRANT SELECT ON TABLE public.ai_category_reports TO aladdin_user;
GRANT SELECT ON TABLE public.parental_reports TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE cleanup.cleanup_records TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE darkweb.darkweb_leaks TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE identity.identity_attempts TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE location.location_requests TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE tracker.tracker_blocks TO aladdin_user;
COMMIT;
