-- Retention policies per domain (safe deletes for stale raw beyond window)
-- Darkweb leaks: keep 365 days
DELETE FROM darkweb.darkweb_leaks WHERE leak_date < NOW() - INTERVAL '365 days';
-- Identity attempts: keep 180 days
DELETE FROM identity.identity_attempts WHERE timestamp < NOW() - INTERVAL '180 days';
-- Tracker blocks: keep 180 days
DELETE FROM tracker.tracker_blocks WHERE last_blocked_at < NOW() - INTERVAL '180 days';
-- Location requests: keep 90 days
DELETE FROM location.location_requests WHERE timestamp < NOW() - INTERVAL '90 days';
-- Cleanup records: keep 365 days
DELETE FROM cleanup.cleanup_records WHERE cleanup_date < NOW() - INTERVAL '365 days';

