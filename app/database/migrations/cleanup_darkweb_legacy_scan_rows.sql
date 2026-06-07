-- Remove orphan scan audit rows from darkweb_leaks (Batch E prod cleanup)
-- Applied after scan_events table is live.

DELETE FROM darkweb.darkweb_leaks
WHERE source IN ('scan_start', 'scan_fast', 'scan_secure')
   OR user_id IS NULL;
